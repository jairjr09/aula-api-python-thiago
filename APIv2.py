from datetime import timedelta

from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError

# Criar aplicação flask
app = Flask(__name__)

# Fazer configuração do token JWT
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['JWT_ACCES_TOKEN_EXPIRES'] = timedelta(minutes=2)
jwt = JWTManager(app)

# Banco de dados fictício
usuarios = {
    "1": {"nome": "Bob Esponja", "email": "cquadrada@bol.com.br", "senha": "1234"},
    "2": {"nome": "Barbie Pedreira", "email": "bs2ken@gmail.com", "senha": "4321"},
    "3": {"nome": "Miranha", "email": "peterparker@uol.com.br", "senha": "mudar123"},
}

# Cria esquema de validação de entradas
class UserSchema(Schema):
    nome = fields.Str(required=True)
    senha = fields.Str(required=True)
    email = fields.Email(required=True)


# Cria rota de login
@app.route('/login', method=['POST'])
def login():
    email = request.json.get('email', None)
    senha = request.json.get('senha', None)

    # Percorre a lista de usuários para verificar se as credenciais existem
    for usuario_id, usuario in usuarios.items():
        if usuario['email'] == email and usuario[senha] == senha:
            access_token = create_access_token(identity=usuario_id)
            return jsonify(access_token=access_token), 200
    return jsonify({"erro":"Credenciais inválidas"}), 401

# Rota para pegar usuário por ID
@app.route("/usuario/<id_usuario>", methods = ['GET'])
def get_usuario(id_usuario):
    # Buscamos um usuário na lista pelo id passado na requisição
    usuario = usuarios.get(id_usuario)
    if usuario:
        return jsonify(usuario),200
    else:
        return jsonify({"erro":"Usuário não encontrado!"}),404

# Rota para cadastrar usuário
@app.route("/usuario",methods = ['POST'])
def criar_usuario():
    # Obter dados vindos da requisição e fazer a validação
    # (baseado no Schema)
    try:
        novo_usuario = UserSchema().load(request.json)
    except ValidationError as erro:
        return jsonify(erro.messages), 400

    # Criar o ID do novo usuário
    id_usuario_novo = str(len(usuarios)+1)
    # Incluímos o novo usuário na lista
    usuarios[id_usuario_novo] = novo_usuario
    return jsonify({"id_usuario":id_usuario_novo}), 201

# Roda a aplicação
if __name__ == '__main__':
    app.run()