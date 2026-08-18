import os 
import random
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash


############################ Debe ejecutarse por terminal de la carpeta " python LogicaNegocio.py " 

negocio = Flask(__name__)
CORS(negocio)

#Diccionario en memoria
codigos_recuperacion = {}

#Configuración del entorno para correo y Método para envio de correo (SMTP)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "edumg1221@gmail.com"             # Coloca aquí tu correo
SENDER_PASSWORD = "fpxt yrry knxc qjvk"          # Coloca aquí tu Contraseña de Aplicación

def enviar_email(destinatario, codigo):
    asunto = "Código de Recuperación de Contraseña"
    cuerpo = f"""
    Hola,

    Has solicitado restablecer tu contraseña.
    Tu código de verificación es: {codigo}

    Si no solicitaste este cambio, ignora este mensaje.
    """
    
    msg = MIMEText(cuerpo)
    msg['Subject'] = asunto
    msg['From'] = SENDER_EMAIL
    msg['To'] = destinatario

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Habilita el cifrado TLS
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False



# BASE DE DATOS TEMPORAL EN MEMORIA (Lista de usuarios para pruebas) 
usuarios_db = [
    {
        "id": 1,
        "username": "admin",
        "email": "admin@sistema.com",
        "password": generate_password_hash("123"),
        "role": "admin"
    }
]

#Encargado del registro de los usuarios al sistema 
@negocio.route('/api/register', methods=['POST'])
def registro():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Validar si el usuario o email ya existen en la lista
    for u in usuarios_db:
        if u['username'] == username:
            return jsonify({"message": "El nombre de usuario ya existe"}), 400
        if u['email'] == email:
            return jsonify({"message": "El correo ya está registrado"}), 400

    # Crear el nuevo usuario simulado
    nuevo_usuario = {
        "id": len(usuarios_db) + 1,
        "username": username,
        "email": email,
        "password": generate_password_hash(password),
        "role": "user"
    }
    
    usuarios_db.append(nuevo_usuario)
    print(" Nuevo usuario agregado: {nuevo_usuario}")

    return jsonify({"message": "Usuario registrado exitosamente",
                   "user": {
                   "id": nuevo_usuario["id"],
                   "username": nuevo_usuario["username"],
                   "email": nuevo_usuario["email"],
                   "role": nuevo_usuario["role"]
                    }
    }), 201

#Encargado del inicio de sesión de los usuarios en el sistema
@negocio.route('/api/login', methods=['POST'])
def inicio_sesion():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Buscar usuario en la lista
    for u in usuarios_db:
        if u['username'] == username and check_password_hash(u['password'], password):
            print("Sesión iniciada para: {username}")
            return jsonify({
                "message": "Inicio de sesión exitoso",
                "user": {
                    "id": u["id"],
                    "username": u["username"],
                    "email": u["email"],
                    "role": u["role"]
                }
            }), 200

    return jsonify({"message": "Usuario o contraseña incorrectos"}), 401

#Encargado de enviar un codigo para recuperar la contraseña 
@negocio.route('/api/forgot-password', methods=['POST'])
def enviar_coodigo():
    data = request.get_json()
    email = data.get('email')

    # 1. Verificar si el correo pertenece a algún usuario
    usuario = next((u for u in usuarios_db if u['email'] == email), None)
    if not usuario:
        return jsonify({"message": "El correo no está registrado"}), 404

    # 2. Generar un código aleatorio de 6 dígitos
    codigo = str(random.randint(100000, 999999))
    codigos_recuperacion[email] = codigo

    # 3. Enviar el correo
    if enviar_email(email, codigo):
        print(f"Código {codigo} enviado exitosamente a {email}")
        return jsonify({"message": "Código enviado correctamente a su correo"}), 200
    else:
        return jsonify({"message": "Error al enviar el correo electrónico"}), 500
    
#Encargado de verificar el codigo enviado 
@negocio.route('/api/verify-code', methods=['POST'])
def verificar_codigo():
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')

    if email in codigos_recuperacion and codigos_recuperacion[email] == code:
        return jsonify({"message": "Código verificado"}), 200

    return jsonify({"message": "Código incorrecto o no encontrado"}), 400

#Encargado de cambiar la contraseña
@negocio.route('/api/reset-password', methods=['POST'])
def cambiar_contrasenna():
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')
    new_password = data.get('new_password')

    if email not in codigos_recuperacion or codigos_recuperacion[email] != code:
        return jsonify({"message": "Código inválido o sesión expirada"}), 400

    # Buscar al usuario por correo y actualizar la contraseña en la BD temporal
    for u in usuarios_db:
        if u['email'] == email:
            u['password'] = generate_password_hash(new_password)
            print(f"Contraseña actualizada para {email}")
            return jsonify({"message": "Contraseña actualizada exitosamente"}), 200

    return jsonify({"message": "Usuario no encontrado"}), 404

#Encargado de obtener todos los usuarios (para el panel de administración)
@negocio.route('/api/users', methods=['GET'])
def get_usuarios():
    # Retorna la lista de usuarios omitiendo la contraseña por seguridad
    usuarios_limpios = [
        {
            "id": u["id"],
            "username": u["username"],
            "email": u["email"],
            "password": "*************", #u["password"],
            "role": u["role"]
        }
        for u in usuarios_db
    ]
    return jsonify(usuarios_limpios), 200

#Encargado de actualizar un usuario por ID
@negocio.route('/api/users/<int:user_id>', methods=['PUT'])
def actualizar_usuario(user_id):
    data = request.get_json()
    for u in usuarios_db:
        if u['id'] == user_id:
            u['username'] = data.get('username', u['username'])
            u['email'] = data.get('email', u['email'])
            u['role'] = data.get('role', u['role'])
            return jsonify({"message": "Usuario actualizado correctamente"}), 200
    return jsonify({"message": "Usuario no encontrado"}), 404

#Encargado de eliminar un usuario por ID
@negocio.route('/api/users/<int:user_id>', methods=['DELETE'])
def eliminar_usuario(user_id):
    global usuarios_db
    usuarios_db = [u for u in usuarios_db if u['id'] != user_id]
    return jsonify({"message": "Usuario eliminado correctamente"}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    negocio.run(host='0.0.0.0', port=port, debug=True)