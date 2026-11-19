"""CRUD de usuarios do sistema (usuario + senha).

A senha e gravada sempre como HASH (generate_password_hash).
As respostas NUNCA incluem a coluna senha.
"""
from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash

from app import banco
from app.erros import resposta_erro
from app.validacao import (
    ErroValidacao,
    exigir_campos,
    exigir_json,
    texto,
    validar_ativo,
    validar_perfil,
    validar_senha,
)

bp = Blueprint('usuarios', __name__)

CAMPOS = 'id, nome_usuario, nome_completo, perfil, ativo, criado_em'


def _validar_nome_usuario(valor):
    nome = texto(valor if isinstance(valor, dict) else {'nome_usuario': valor},
                 'nome_usuario', 50)
    if ' ' in nome:
        raise ErroValidacao('Nome de usuario nao pode conter espacos.')
    return nome


@bp.get('/api/usuarios')
def listar_usuarios():
    """Lista os usuarios (sem a senha). Aceita ?busca=xxx."""
    busca = (request.args.get('busca') or '').strip()
    sql = f'SELECT {CAMPOS} FROM usuarios'
    params = []
    if busca:
        sql += ' WHERE nome_usuario LIKE %s OR nome_completo LIKE %s'
        like = f'%{busca}%'
        params.extend([like, like])
    sql += ' ORDER BY nome_usuario ASC'
    linhas = banco.consultar(sql, params)
    return jsonify({'total': len(linhas), 'dados': linhas})


@bp.get('/api/usuarios/<int:registro_id>')
def buscar_usuario(registro_id):
    """Busca um usuario pelo id (sem a senha)."""
    linha = banco.consultar_um(
        f'SELECT {CAMPOS} FROM usuarios WHERE id = %s', (registro_id,)
    )
    if not linha:
        return resposta_erro('Usuario nao encontrado.', 404)
    return jsonify({'dados': linha})


@bp.post('/api/usuarios')
def criar_usuario():
    """Cadastra um novo usuario com senha criptografada."""
    dados = request.get_json(silent=True)
    exigir_campos(dados, ['nome_usuario', 'senha', 'nome_completo'])

    nome_usuario = _validar_nome_usuario(dados['nome_usuario'])
    senha = validar_senha(dados['senha'])
    nome_completo = texto(dados, 'nome_completo', 100)
    perfil = validar_perfil(dados.get('perfil'))
    ativo = validar_ativo(dados.get('ativo'))

    resultado = banco.executar(
        'INSERT INTO usuarios '
        '(nome_usuario, senha, nome_completo, perfil, ativo) '
        'VALUES (%s, %s, %s, %s, %s)',
        (nome_usuario, generate_password_hash(senha),
         nome_completo, perfil, ativo),
    )
    return jsonify({
        'mensagem': 'Usuario criado com sucesso.',
        'dados': {'id': resultado['ultimo_id']},
    }), 201


@bp.put('/api/usuarios/<int:registro_id>')
def atualizar_usuario(registro_id):
    """Edita um usuario. A senha so muda se o campo for enviado."""
    if not banco.consultar_um(
        'SELECT id FROM usuarios WHERE id = %s', (registro_id,)
    ):
        return resposta_erro('Usuario nao encontrado.', 404)

    dados = request.get_json(silent=True)
    exigir_json(dados)

    campos = {}
    if 'nome_usuario' in dados:
        campos['nome_usuario'] = _validar_nome_usuario(dados['nome_usuario'])
    if 'senha' in dados and str(dados.get('senha') or '').strip():
        campos['senha'] = generate_password_hash(validar_senha(dados['senha']))
    if 'nome_completo' in dados:
        campos['nome_completo'] = texto(dados, 'nome_completo', 100)
    if 'perfil' in dados:
        campos['perfil'] = validar_perfil(dados['perfil'])
    if 'ativo' in dados:
        campos['ativo'] = validar_ativo(dados['ativo'])

    if not campos:
        raise ErroValidacao('Informe ao menos um campo para atualizar.')

    sql = ('UPDATE usuarios SET '
           + ', '.join(f'{nome_campo} = %s' for nome_campo in campos)
           + ' WHERE id = %s')
    banco.executar(sql, (*campos.values(), registro_id))

    atualizado = banco.consultar_um(
        f'SELECT {CAMPOS} FROM usuarios WHERE id = %s', (registro_id,)
    )
    return jsonify({
        'mensagem': 'Usuario atualizado com sucesso.',
        'dados': atualizado,
    })


@bp.delete('/api/usuarios/<int:registro_id>')
def excluir_usuario(registro_id):
    """Exclui um usuario do sistema."""
    resultado = banco.executar(
        'DELETE FROM usuarios WHERE id = %s', (registro_id,)
    )
    if resultado['linhas_afetadas'] == 0:
        return resposta_erro('Usuario nao encontrado.', 404)
    return jsonify({'mensagem': 'Usuario excluido com sucesso.'})
