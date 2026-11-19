"""Autenticacao: login de usuarios da clinica.

A senha NUNCA e comparada em texto puro: o banco guarda o HASH
(gerado pelo werkzeug) e aqui usamos check_password_hash para
conferir se a senha digitada bate com o hash armazenado.
"""
from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash

from app import banco
from app.erros import resposta_erro
from app.validacao import exigir_campos

bp = Blueprint('auth', __name__)


@bp.post('/api/auth/login')
def login():
    """Recebe {nome_usuario, senha} e valida o acesso."""
    dados = request.get_json(silent=True)
    exigir_campos(dados, ['nome_usuario', 'senha'])

    usuario = banco.consultar_um(
        'SELECT id, nome_usuario, senha, nome_completo, perfil, ativo '
        'FROM usuarios WHERE nome_usuario = %s',
        (str(dados['nome_usuario']).strip(),),
    )

    if not usuario or not check_password_hash(
        usuario['senha'], str(dados['senha'])
    ):
        # Mesma mensagem para login inexistente ou senha errada:
        # nao se deve revelar qual dos dois estava incorreto.
        return resposta_erro('Usuario ou senha invalidos.', 401)

    if not usuario['ativo']:
        return resposta_erro('Usuario desativado. Contate o administrador.', 403)

    del usuario['senha']  # nunca devolve o hash para o cliente
    return jsonify({
        'mensagem': 'Login realizado com sucesso.',
        'dados': usuario,
    })
