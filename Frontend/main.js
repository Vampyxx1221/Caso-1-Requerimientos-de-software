// URL base de tu API Backend
const API_URL = "http://localhost:5000/api"; 

document.addEventListener("DOMContentLoaded", () => {

    // 1. Manejo de Registro
    const formRegistro = document.getElementById("form-registro");
    if (formRegistro) {
        formRegistro.addEventListener("submit", async (e) => {
            e.preventDefault();
            const data = {
                username: e.target.username.value,
                email: e.target.email.value,
                password: e.target.password.value
            };

            try {
                const response = await fetch(`${API_URL}/register`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                if (response.ok) {
                    localStorage.setItem("user", JSON.stringify(result.user));

                    // Redirigir directamente según el rol
                    if (result.user.role === "admin") {
                         window.location.href = "UsuarioAdministrador.html";
                    } else {
                         window.location.href = "UsuarioNormal.html";
                }
                } else {
                    alert(result.message || "Error al registrar");
                }
            } catch (error) {
                console.error("Error al conectar con el servidor:", error);
            }
        });
    }

    // 2. Manejo de Inicio de Sesión
    const formLogin = document.getElementById("form-login");
    if (formLogin) {
        formLogin.addEventListener("submit", async (e) => {
            e.preventDefault();
            const data = {
                username: e.target.username.value,
                password: e.target.password.value
            };

            try {
                const response = await fetch(`${API_URL}/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data)
                });

                const result = await response.json();
                if (response.ok) {
                    // Guardar token/sesión en localStorage si aplica
                    localStorage.setItem("user", JSON.stringify(result.user));
                    
                    // Redirección según el rol retornado por el backend
                    if (result.user.role === "admin") {
                        window.location.href = "UsuarioAdministrador.html";
                    } else {
                        window.location.href = "UsuarioNormal.html";
                    }
                } else {
                    alert(result.message || "Credenciales incorrectas");
                }
            } catch (error) {
                console.error("Error en la autenticación:", error);
            }
        });
    }

    const formSolicitarCodigo = document.getElementById("form-solicitar-codigo");
    if (formSolicitarCodigo) {
        formSolicitarCodigo.addEventListener("submit", async (e) => {
            e.preventDefault();
            const data = { email: e.target.email.value };

            try {
                const response = await fetch(`${API_URL}/forgot-password`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                if (response.ok) {
                    alert("Código enviado a su correo");

                    const seccionVerificar = document.getElementById("seccion-verificar");
                    if (seccionVerificar) {
                        seccionVerificar.style.display = "block";
                    }
                } else {
                    alert(result.message || "Error al solicitar código");
                }
            } catch (error) {
                console.error("Error en la solicitud:", error);
            }
        });
    }

    const formVerificarCodigo = document.getElementById("form-verificar-codigo");
    if (formVerificarCodigo) {
        formVerificarCodigo.addEventListener("submit", async (e) => {
            e.preventDefault();
            const data = { code: e.target.code.value };

            try {
                const response = await fetch(`${API_URL}/verify-code`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                if (response.ok) {
                    alert("Código verificado correctamente");
                } else {
                    alert(result.message || "Código inválido");
                }
            } catch (error) {
                console.error("Error al verificar código:", error);
            }
        });
    }

    // 4. Cargar Tabla de Usuarios en el Panel de Administrador
const tablaUsuarios = document.getElementById("tabla-usuarios");
if (tablaUsuarios) {
    fetch(`${API_URL}/users`)
        .then(response => response.json())
        .then(users => {
            tablaUsuarios.innerHTML = "";
            users.forEach(u => {
                const fila = `
                    <tr>
                        <td>${u.id}</td>
                        <td>${u.username}</td>
                        <td>${u.email}</td>
                        <td><span class="role-badge ${u.role}">${u.role}</span></td>
                        <td>Activo</td>
                        <td>
                            <button class="btn-action edit">Editar</button>
                            <button class="btn-action delete">Eliminar</button>
                        </td>
                    </tr>
                `;
                tablaUsuarios.innerHTML += fila;
            });
        })
        .catch(error => console.error("Error al cargar la tabla de usuarios:", error));
}

    // 3. Cargar Datos en el Dashboard Normal
    const infoUsername = document.getElementById("info-username");
    if (infoUsername) {
        const user = JSON.parse(localStorage.getItem("user"));
        if (user) {
            document.getElementById("info-username").textContent = user.username;
            document.getElementById("info-email").textContent = user.email;
            document.getElementById("user-role").textContent = user.role;
        } else {
            window.location.href = "IniciarSesion.html";
        }
    }
});