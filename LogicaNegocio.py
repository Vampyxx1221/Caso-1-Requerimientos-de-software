import os 
from flask import Flask, request, jsonify
from flask_cors import CORS

negocio = Flask(__name__)
CORS(negocio)

# BASE DE DATOS TEMPORAL EN MEMORIA (Lista de usuarios para pruebas)
usuarios_db = [
    {
        "id": 1,
        "username": "admin",
        "email": "admin@sistema.com",
        "password": "123",
        "role": "admin"
    }
]

# 1. Se encarga del registro de los usuarios al sistema 
@negocio.route('/api/register', methods=['POST'])
def register():
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
        "password": password,
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


# 2. Se encarga del inicio de sesión de los usuarios en el sistema
@negocio.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Buscar usuario en la lista
    for u in usuarios_db:
        if u['username'] == username and u['password'] == password:
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


# 3. Se encarga de enviar un codigo para recuperar la contraseña 
@negocio.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    print("solicitar código para: {email}")
    return jsonify({"message": "Código enviado correctamente"}), 200


# 4. Se encarga de verificar el codigo enviado 
@negocio.route('/api/verify-code', methods=['POST'])
def verify_code():
    data = request.get_json()
    code = data.get('code')
    print("Código recibido: {code}")
    return jsonify({"message": "Código verificado"}), 200

# 5. Obtener todos los usuarios (para el panel de administración)
@negocio.route('/api/users', methods=['GET'])
def get_users():
    # Retorna la lista de usuarios omitiendo la contraseña por seguridad
    usuarios_limpios = [
        {
            "id": u["id"],
            "username": u["username"],
            "email": u["email"],
            "role": u["role"]
        }
        for u in usuarios_db
    ]
    return jsonify(usuarios_limpios), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    negocio.run(host='0.0.0.0', port=port, debug=True)