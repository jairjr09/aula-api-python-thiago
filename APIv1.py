from flask import Flask, jsonify, request

# Criar aplicação flask
app = Flask(__name__)

# Banco de dados fictício
usuarios = {
    "1":{"nome":"Bob Esponja","email":"cquadrada@bol.com.br","senha":"1234"},
    "2":{"nome":"Barbie Pedreira","email":"bs2ken@gmail.com","senha":"4321"},
    "3":{"nome":"Miranha","email":"peterparker@uol.com.br","senha":"mudar123"},
}

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
    # Armazenamos os dados vindos do body da requisição da variável
    novo_usuario = request.json
    # Criar o ID do novo usuário
    id_usuario_novo = str(len(usuarios)+1)
    # Incluímos o novo usuário na lista
    usuarios[id_usuario_novo] = novo_usuario
    return jsonify({"id_usuario":id_usuario_novo}), 201

# Roda a aplicação
if __name__ == '__main__':
    app.run()