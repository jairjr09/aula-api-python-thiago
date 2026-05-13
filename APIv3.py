from collections import defaultdict
from datetime import timedelta, datetime

from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError

# Criar aplicação flask
app = Flask(__name__)

# Fazer configuração do token JWT
# Em produção NUNCA deixe essa chave hard coded!
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

# Cria lista de tentativas de login erradas
tentativas_login_falha = defaultdict(list)

# Configurar constantes de proteção contra força bruta
MAX_TENTATIVAS_LOGIN = 3
TEMPO_BLOCK_MINUTOS = 1

#Função que verifica se o IP está bloqueado por excesso de tentativas
def is_blocked(ip):
    if ip in tentativas_login_falha:
        tentativas = tentativas_login_falha[ip]
        #Remover tentativas antigas
        tentativas = [tentativas for tentativa in tentativas if
                      datetime.now() - tentativa < timedelta(minutes = TEMPO_BLOCK_MINUTOS)]
        tentativas_login_falha[ip] = tentativas


        # Se o número de tentativas erradas exceder o limite, bloqueia o IP!
        if len(tentativas) >= MAX_TENTATIVAS_LOGIN:
            return True # Bloqueado, MANÉ!

    return False

# Cria rota de login
@app.route('/login', methods=['POST'])
def login():
    # Obtém o IP do usuário para verificação
    ip = request.remote_addr

    # Verifica se o IP está bloqueado
    if is_blocked(ip):
        return jsonify({"erro":"Excesso de tentativas erradas. Tente novamente mais tarde"})

    # Obtemos as credenciais informadas pelo usuário
    email = request.json.get('email',None)
    senha = request.json.get('senha',None)

    # Percorre a lista de usuários para verificar se as credenciais existem
    for usuario_id, usuario in usuarios.items():
        if usuario['email'] == email and usuario['senha'] == senha:
            access_token = create_access_token(identity=usuario_id)
            return jsonify(access_token=access_token), 200

    tentativas_login_falha[ip].append(datetime.now())
    return jsonify({"erro":"Credenciais inválidas"}), 401

# Rota para pegar usuário por ID
@app.route("/usuario/<id_usuario>", methods = ['GET'])
@jwt_required
def get_usuario(id_usuario):
    # Verificamos o token JWT do usuário logado
    id_usuario_atual = get_jwt_identity()
    if id_usuario_atual != id_usuario:
        return jsonify({"erro":"Não autorizado!"}), 403

    # Buscamos um usuário na lista pelo id passado na requisição
    usuario = usuarios.get(id_usuario)
    if usuario:
        dados_usuarios = {**usuario}
        dados_usuarios.pop("senha", None)
        return jsonify(dados_usuarios),200
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