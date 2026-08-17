import os 
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash


############################ Debe ejecutarse por terminal de la carpeta " python LogicaNegocio.py " 

negocio = Flask(__name__)
CORS(negocio)

# BASE DE DATOS TEMPORAL EN MEMORIA (Lista de usuarios para pruebas) [Cambiar a una real]
usuarios_db = [
    {
        "id": 1,
        "username": "admin",
        "email": "admin@sistema.com",
        "password": "123",
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
    print("solicitar código para: {email}")
    return jsonify({"message": "Código enviado correctamente"}), 200

#Encargado de verificar el codigo enviado 
@negocio.route('/api/verify-code', methods=['POST'])
def verificar_codigo():
    data = request.get_json()
    code = data.get('code')
    print("Código recibido: {code}")
    return jsonify({"message": "Código verificado"}), 200

#Encargado de cambiar la contraseña
@negocio.route('/api/reset-password', methods=['POST'])
def cambiar_contrasenna():
    data = request.get_json()
    email = data.get('email')
    new_password = data.get('new_password')

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