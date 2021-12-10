import json
from werkzeug.security import generate_password_hash, check_password_hash

import jwt
from flask import Flask, Response, request
from flask_restful import Resource, Api, request
from flask_cors import CORS, cross_origin
from model import Usuario
from flask.json import jsonify

app = Flask(__name__)
CORS(app)
api = Api(app)

class Pessoa(Resource):
    def get(self):
        try:

            token = request.headers.get('authorization') 
            key = request.headers.get('x-api-key')
            payload = jwt.decode(token, key, algorithms=["HS256"])
            id = payload['id']

            pessoa = Usuario.query.filter_by(id=id).first()
            response = {
                'id': pessoa.id,
                'nome': pessoa.nome,
                'idade': pessoa.idade,
                'email': pessoa.email,
                'senha': pessoa.senha
            }
            return response
        except:
            return { 'erro': 'Nenhum usuario identificado com o id informado.'}

    def delete(self, id):
        try:
            pessoa = Usuario.query.filter_by(id=id).first()
            pessoa.delete()
            return resposta(200, "Deleção Usuário", pessoa.to_json())  
        except Exception as e:
            print('Erro ', e)
            return resposta(400, "Deleção Usuário", {}, "Erro ao deletar usuário")    

    def put(self, id):

        pessoa = Usuario.query.filter_by(id=id).first()
        body = request.get_json()

        try:
            if('nome' in body):
                pessoa.nome = body['nome']
            if('idade' in body):
                pessoa.idade = body['idade']
            if('email' in body):
                pessoa.email = body['email'] 
            if('senha' in body):
                pessoa.senha = body['senha']    

            pessoa.save()

            return resposta(200, 'Alterar Usuário', pessoa.to_json, 'Usuário alterado com sucesso!')
        except Exception as e:
            print('Erro ', e)
            return resposta(400, "Alterar usuário", {}, "Erro ao alterar o usuário!")          


class Pessoas(Resource):
    def get(self):
        pessoas = Usuario.query.all()
        pessoas_json = [pessoa.to_json() for pessoa in pessoas]
        return resposta(200, "usuarios", pessoas_json)

    def post(self):
        try:
            body = request.get_json()
            pessoa = Usuario(nome = body['nome'] , idade = body['idade'], email = body['email'], senha = generate_password_hash(body['senha']));
            pessoa.save()
            return resposta(201, 'Usuário', pessoa.to_json(), 'Usuário Criado com sucesso')
        except Exception as e:
            print('Erro: ', e)
            return resposta(400, 'Usuário', {}, 'Erro ao cadastrar')        


class Auth(Resource):
    def post(self):
        try:
            key = "senhaSuperSecretaESegura" #tem que ser requisitada para gerar um token
            
            usuarioRequest = json.loads(request.data)
  
            usuario = Usuario.query.filter_by(email=usuarioRequest['email']).first()  

            # senhaRequisicao = generate_password_hash(usuarioRequest["senha"])
            
            if(check_password_hash(usuario.senha, usuarioRequest["senha"]) and usuarioRequest['email'] == usuario.email): # compara o hash com a senha requisitada
                payload = {
                    "id": usuario.id,
                }
                jwtToken = jwt.encode(payload, key, algorithm="HS256") # key precisa vim da requisição
    
                return resposta(201, 'token', jwtToken, 'Usuário autenticado')

            else:
                return resposta(404, "Erro", "Usuário ou senha incorretos!")
                #{"erro": "email ou senha incorretos"}    
        except:
            return resposta(400, "Erro requisição", "Algum erro ocorreu!")
            # {"error": "Bad request"}

    def get(self):
        try:
            # essa rota é utilizada para validar o token e também retornar alguma informação
            # é possivel validar o token no front
            token = request.headers.get('authorization') 
            key = request.headers.get('x-api-key')
            payload = jwt.decode(token, key, algorithms=["HS256"])
            
            return resposta(200, 'payload', payload)
            #{"status": "ok", "payload": payload}
        except:
            return {"error": "deu ruim"}


def resposta(status, nome_do_conteudo, conteudo, mensagem=False):
    body = {}
    body[nome_do_conteudo] = conteudo

    if(mensagem):

        body["mensagem"] = mensagem

    return Response(json.dumps(body), status=status, mimetype="application/json")

api.add_resource(Pessoa, '/pessoa')
api.add_resource(Pessoas, '/pessoas')
api.add_resource(Auth, '/autenticar')

if __name__ == '__main__':
    app.run(debug=True)