import os 
import random
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

negocio = Flask(__name__)
CORS(negocio)

# Configuración de la base de datos sqlite
negocio.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sistema.db'
negocio.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(negocio)

# Modelo de base de datos. sqlalchemy permite manejar objetos de python como tablas de sql 
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    intentos_fallidos = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

# Crear la base de datos y un usuario administrador por defecto
with negocio.app_context():
    db.create_all()
    if not Usuario.query.filter_by(username="admin").first():
        admin_default = Usuario(
            username="admin",
            email="admin@sistema.com",
            password=generate_password_hash("123"),
            role="admin"
        )
        db.session.add(admin_default)
        db.session.commit()

# Diccionario en memoria solo para los códigos de correo
codigos_recuperacion = {}

# Configuración para enviar correos
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "loginsys1221@gmail.com"
SENDER_PASSWORD = "gwjv kzrj jjwy fezy"
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
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False

# Rutas de API

#Método para el resgitro de un usuario al sistema
@negocio.route('/api/register', methods=['POST'])
def registro():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if Usuario.query.filter_by(username=username).first():
        return jsonify({"message": "El nombre de usuario ya existe"}), 400
    if Usuario.query.filter_by(email=email).first():
        return jsonify({"message": "El correo ya está registrado"}), 400

    nuevo_usuario = Usuario(
        username=username,
        email=email,
        password=generate_password_hash(password),
        role="user"
    )
    
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({
        "message": "Usuario registrado exitosamente",
        "user": {
            "id": nuevo_usuario.id,
            "username": nuevo_usuario.username,
            "email": nuevo_usuario.email,
            "role": nuevo_usuario.role
        }
    }), 201

#Método para iniciar sesión de un usuario ya registrado 
@negocio.route('/api/login', methods=['POST'])
def inicio_sesion():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    usuario = Usuario.query.filter_by(username=username).first()
    if not usuario:
        return jsonify({"message": "Usuario o contraseña incorrectos"}), 401

    # Verificar si está inactivo/bloqueado
    if not usuario.is_active:
        return jsonify({"message": "Su cuenta está inactiva/bloqueada. Contacte al administrador."}), 403

    # Comprobar contraseña
    if check_password_hash(usuario.password, password):
        usuario.intentos_fallidos = 0  # Reiniciar contador en éxito
        db.session.commit()
        return jsonify({
            "message": "Inicio de sesión exitoso",
            "user": {
                "id": usuario.id,
                "username": usuario.username,
                "email": usuario.email,
                "role": usuario.role
            }
        }), 200
    else:
        usuario.intentos_fallidos += 1
        if usuario.intentos_fallidos >= 3:
            usuario.is_active = False
            db.session.commit()
            return jsonify({"message": "Ha superado los 3 intentos fallidos. Su cuenta ha sido inactivada."}), 403
        
        db.session.commit()
        intentos_restantes = 3 - usuario.intentos_fallidos
        return jsonify({"message": f"Contraseña incorrecta. Le quedan {intentos_restantes} intento(s)."}), 401

    return jsonify({"message": "Usuario o contraseña incorrectos"}), 401

#Método para enviar un codigo por corre0
@negocio.route('/api/forgot-password', methods=['POST'])
def enviar_codigo():
    data = request.get_json()
    email = data.get('email')

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({"message": "El correo no está registrado"}), 404

    codigo = str(random.randint(100000, 999999))
    codigos_recuperacion[email] = codigo

    if enviar_email(email, codigo):
        return jsonify({"message": "Código enviado correctamente a su correo"}), 200
    else:
        return jsonify({"message": "Error al enviar el correo electrónico"}), 500

#Método para verificar el correo 
@negocio.route('/api/verify-code', methods=['POST'])
def verificar_codigo():
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')

    if email in codigos_recuperacion and codigos_recuperacion[email] == code:
        return jsonify({"message": "Código verificado"}), 200

    return jsonify({"message": "Código incorrecto o no encontrado"}), 400

#Método para cambiar la contraseña
@negocio.route('/api/reset-password', methods=['POST'])
def cambiar_contrasenna():
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')
    new_password = data.get('new_password')

    if email not in codigos_recuperacion or codigos_recuperacion[email] != code:
        return jsonify({"message": "Código inválido o sesión expirada"}), 400

    usuario = Usuario.query.filter_by(email=email).first()
    if usuario:
        usuario.password = generate_password_hash(new_password)
        db.session.commit()
        del codigos_recuperacion[email]
        return jsonify({"message": "Contraseña actualizada exitosamente"}), 200

    return jsonify({"message": "Usuario no encontrado"}), 404

#Método para mostrar los usuarios
@negocio.route('/api/users', methods=['GET'])
def get_usuarios():
    usuarios = Usuario.query.all()
    usuarios_limpios = [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "password": "*************",
            "role": u.role,
            "is_active": u.is_active,
            "intentos_fallidos": u.intentos_fallidos
        }
        for u in usuarios
    ]
    return jsonify(usuarios_limpios), 200
   
#Métodos para la modificaciones en los usuarios registrados
@negocio.route('/api/users/<int:user_id>', methods=['PUT'])
def actualizar_usuario(user_id):
    data = request.get_json()
    usuario = Usuario.query.get(user_id)
    if usuario:
        usuario.username = data.get('username', usuario.username)
        usuario.email = data.get('email', usuario.email)
        usuario.role = data.get('role', usuario.role)
        db.session.commit()
        return jsonify({"message": "Usuario actualizado correctamente"}), 200
    return jsonify({"message": "Usuario no encontrado"}), 404

@negocio.route('/api/users/<int:user_id>', methods=['DELETE'])
def eliminar_usuario(user_id):
    usuario = Usuario.query.get(user_id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({"message": "Usuario eliminado correctamente"}), 200
    return jsonify({"message": "Usuario no encontrado"}), 404

@negocio.route('/api/users/<int:user_id>/toggle-status', methods=['PATCH'])
def cambiar_estado_usuario(user_id):
    data = request.get_json()
    usuario = Usuario.query.get(user_id)
    if usuario:
        usuario.is_active = data.get('is_active', not usuario.is_active)
        if usuario.is_active:
            usuario.intentos_fallidos = 0  # Desbloquear reinicia contadores
        db.session.commit()
        estado_str = "activado" if usuario.is_active else "inactivado"
        return jsonify({"message": f"Usuario {estado_str} correctamente"}), 200
    return jsonify({"message": "Usuario no encontrado"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    negocio.run(host='0.0.0.0', port=port, debug=True)