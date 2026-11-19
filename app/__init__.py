"""Fabrica da aplicacao Flask (app factory).

Padrao factory: a app e criada por uma funcao, o que deixa o codigo
organizado e permite criar instancias diferentes (testes, producao...).
"""
from flask import Flask, jsonify
from flask_cors import CORS

from app import banco
from app.config import Config
from app.erros import registrar_tratadores


def create_app():
    """Cria e configura a aplicacao da API."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Libera a API para qualquer origem (necessario quando o front-end
    # roda em outra porta/pasta, por exemplo em um servidor estatico)
    CORS(app, resources={r'/api/*': {'origins': '*'}})

    # Pool de conexoes com o MySQL
    banco.iniciar_pool(app)

    # Rotas (Blueprints - um modulo por recurso)
    from app.rotas import registrar_blueprints
    registrar_blueprints(app)

    # Respostas de erro padronizadas em JSON
    registrar_tratadores(app)

    # Informacoes da API (a raiz "/" entrega o front-end)
    @app.get('/api/status')
    def status_api():
        return jsonify({
            'sistema': 'API Clinica Odontologica',
            'versao': '1.0.0',
            'status': 'online',
            'mensagem': 'Bem-vindo a API da Clinica Odontologica.',
            'front_end': '/',
            'guia_integracao': 'docs/03-guia-integracao-front-end.md',
            'recursos': {
                'painel': '/api/painel/resumo',
                'login': 'POST /api/auth/login',
                'pacientes': '/api/pacientes',
                'dentistas': '/api/dentistas',
                'procedimentos': '/api/procedimentos',
                'consultas': '/api/consultas',
                'usuarios': '/api/usuarios',
            },
        })

    return app
