// URL base de tu API Backend
const API_URL = "http://localhost:5000/api"; 

//Método para transferir información 
async function apiFetch(endpoint, method = "GET", data = null) {
    const options = {
          method,
          headers: { "Content-Type": "application/json" }
    };
    if (data) options.body = JSON.stringify(data);

    const response = await fetch(`${API_URL}${endpoint}`, options);
    const result = await response.json();

    if (!response.ok) {
        throw new Error(result.message || "Error en la petición");
    }
    return result;
}
//Redirecciona el dashboard según el tipo de usuario 
function redirigirPorRol(role) {
    if (role === "admin") {
        window.location.href = "UsuarioAdministrador.html";
    } else {
        window.location.href = "UsuarioNormal.html";
    }
}


//Método para validar la fortaleza de la contraseña
function validarPassword(password) {
    // Permite cualquier carácter especial de la lista extendida
    const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&.#_\-+=\\/<>{}\[\]()~^|:;,])[A-Za-z\d@$!%*?&.#_\-+=\\/<>{}\[\]()~^|:;,]{8,}$/;
    return regex.test(password);
}

//Método para el registro de usuarios 
function registroUsuario() {
    const formRegistro = document.getElementById("form-registro");
    if (!formRegistro) return;

    formRegistro.addEventListener("submit", async (e) => {
        e.preventDefault();
        const password = e.target.password.value;

        if (!validarPassword(password)) {
            alert("La contraseña debe tener al menos 8 caracteres, incluyendo una mayúscula, una minúscula, un número y un carácter especial.");
            return;
        }

        const data = {
            username: e.target.username.value,
            email: e.target.email.value,
            password: password
        };

        try {
            const result = await apiFetch("/register", "POST", data);
            localStorage.setItem("user", JSON.stringify(result.user));
            redirigirPorRol(result.user.role);
        } catch (error) {
            alert(error.message);
            console.error("Error al registrar:", error);
        }
    });
}

//Método para el inicio de sesion 
function iniciarSesion() {
    const formLogin = document.getElementById("form-login");
    if (!formLogin) return;

    formLogin.addEventListener("submit", async (e) => {
        e.preventDefault();
        const data = {
            username: e.target.username.value,
            password: e.target.password.value
        };

        try {
            const result = await apiFetch("/login", "POST", data);
            localStorage.setItem("user", JSON.stringify(result.user));
            redirigirPorRol(result.user.role);
        } catch (error) {
            alert(error.message);
            console.error("Error en la autenticación:", error);
        }
    });
}

//Método para recuperación, verificación y confirmación de contraseña 
function nuevaContrasenna() {
    // 1: Solicitar el código
    const formSolicitarCodigo = document.getElementById("form-solicitar-codigo");
    if (formSolicitarCodigo) {
        formSolicitarCodigo.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = e.target.email.value;
            localStorage.setItem("reset_email", email);

            try {
                await apiFetch("/forgot-password", "POST", { email });
                alert("Código enviado exitosamente a su correo");

                const seccionVerificar = document.getElementById("seccion-verificar");
                if (seccionVerificar) seccionVerificar.style.display = "block";
            } catch (error) {
                alert(error.message);
                console.error("Error en la solicitud:", error);
            }
        });
    }

    // 2: Verificar Código
    const formVerificarCodigo = document.getElementById("form-verificar-codigo");
    if (formVerificarCodigo) {
        formVerificarCodigo.addEventListener("submit", async (e) => {
            e.preventDefault();
            const code = e.target.code.value;
            const email = localStorage.getItem("reset_email");

            try {
                await apiFetch("/verify-code", "POST", { email, code });
                alert("Código verificado correctamente");
                localStorage.setItem("reset_code", code);
                window.location.href = "contraseñaNueva.html";
            } catch (error) {
                alert(error.message);
                console.error("Error al verificar código:", error);
            }
        });
    }

    // 3: Establecer Nueva Contraseña
    const formSolicitarContraNueva = document.getElementById("form-solicitar-contra-nueva");
    if (formSolicitarContraNueva) {
        formSolicitarContraNueva.addEventListener("submit", async (e) => {
            e.preventDefault();

            const pass1 = document.getElementById("new-password").value;
            const pass2 = document.getElementById("new-password-veri").value;

            if (pass1 !== pass2) {
                alert("Las contraseñas no coinciden. Por favor verifíquelas.");
                return;
            }

            if (!validarPassword(pass1)) {
                alert("La contraseña debe tener al menos 8 caracteres, incluyendo una mayúscula, una minúscula, un número y un carácter especial.");
                return;
            }

            const data = {
                email: localStorage.getItem("reset_email"),
                code: localStorage.getItem("reset_code"),
                new_password: pass1
            };

            try {
                await apiFetch("/reset-password", "POST", data);
                alert("¡Contraseña actualizada exitosamente! Inicie sesión nuevamente.");
                localStorage.removeItem("reset_email");
                localStorage.removeItem("reset_code");
                window.location.href = "IniciarSesion.html";
            } catch (error) {
                alert(error.message);
                console.error("Error al actualizar contraseña:", error);
            }
        });
    }
}

//Método para mostrar la tabla de usuarios
async function mostrarUsuarios() {
    const tablaUsuarios = document.getElementById("tabla-usuarios");
    if (!tablaUsuarios) return;

    try {
        const users = await apiFetch("/users");
        tablaUsuarios.innerHTML = "";
        users.forEach(u => {
            const fila = `
                <tr>
                    <td>${u.id}</td>
                    <td>${u.username}</td>
                    <td>${u.email}</td>
                    <td>${u.password}</td>
                    <td><span class="role-badge ${u.role}">${u.role}</span></td>
                    <td>Activo</td>
                    <td>
                        <button class="btn-action edit" onclick="editarUsuario(${u.id}, '${u.username}', '${u.email}')">Editar</button>
                        <button class="btn-action delete" onclick="eliminarUsuario(${u.id})">Eliminar</button>
                    </td>
                </tr>
            `;
            tablaUsuarios.innerHTML += fila;
        });
    } catch (error) {
        console.error("Error al cargar la tabla de usuarios:", error);
    }
}

//Métodos para las acciones de la tabla
async function eliminarUsuario(id) {
    if (confirm(`¿Está seguro de eliminar al usuario con ID ${id}?`)) {
        try {
            const result = await apiFetch(`/users/${id}`, "DELETE");
            alert(result.message);
            mostrarUsuarios(); // Recarga la tabla
        } catch (error) {
            alert(error.message);
        }
    }
}
async function editarUsuario(id, usernameActual, emailActual) {
    const nuevoUsername = prompt("Nuevo nombre de usuario:", usernameActual);
    const nuevoEmail = prompt("Nuevo correo electrónico:", emailActual);

    if (nuevoUsername && nuevoEmail) {
        try {
            const result = await apiFetch(`/users/${id}`, "PUT", {
                username: nuevoUsername,
                email: nuevoEmail
            });
            alert(result.message);
            mostrarUsuarios(); // Recarga la tabla
        } catch (error) {
            alert(error.message);
        }
    }
}

//Método para mostrar información del usuario actual 
function infoUsuario() {
    const infoUsername = document.getElementById("info-username");
    if (!infoUsername) return;

    const user = JSON.parse(localStorage.getItem("user"));
    if (user) {
        document.getElementById("info-username").textContent = user.username;
        document.getElementById("info-email").textContent = user.email;
        document.getElementById("user-role").textContent = user.role;
    } else {
        window.location.href = "IniciarSesion.html";
    }
}



document.addEventListener("DOMContentLoaded", () => {
    registroUsuario();
    iniciarSesion();
    nuevaContrasenna();
    mostrarUsuarios();
    infoUsuario();
});


