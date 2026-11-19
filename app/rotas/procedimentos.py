"""CRUD de procedimentos (catalogo de servicos da clinica)."""
from flask import Blueprint, jsonify, request

from app import banco
from app.erros import resposta_erro
from app.validacao import (
    ErroValidacao,
    exigir_campos,
    exigir_json,
    texto,
    validar_inteiro,
    validar_preco,
)

bp = Blueprint('procedimentos', __name__)

CAMPOS = 'id, nome, descricao, preco, duracao_minutos, criado_em'


@bp.get('/api/procedimentos')
def listar_procedimentos():
    """Lista procedimentos. Aceita ?busca=xxx (nome/descricao)."""
    busca = (request.args.get('busca') or '').strip()
    sql = f'SELECT {CAMPOS} FROM procedimentos'
    params = []
    if busca:
        sql += ' WHERE nome LIKE %s OR descricao LIKE %s'
        like = f'%{busca}%'
        params.extend([like, like])
    sql += ' ORDER BY nome ASC'
    linhas = banco.consultar(sql, params)
    return jsonify({'total': len(linhas), 'dados': linhas})


@bp.get('/api/procedimentos/<int:registro_id>')
def buscar_procedimento(registro_id):
    """Busca um procedimento pelo id."""
    linha = banco.consultar_um(
        f'SELECT {CAMPOS} FROM procedimentos WHERE id = %s', (registro_id,)
    )
    if not linha:
        return resposta_erro('Procedimento nao encontrado.', 404)
    return jsonify({'dados': linha})


@bp.post('/api/procedimentos')
def criar_procedimento():
    """Cadastra um novo procedimento."""
    dados = request.get_json(silent=True)
    exigir_campos(dados, ['nome', 'preco'])

    nome = texto(dados, 'nome', 80)
    descricao = texto(dados, 'descricao', 200, obrigatorio=False)
    preco = validar_preco(dados['preco'])
    duracao = validar_inteiro(
        dados.get('duracao_minutos', 30), 'duracao_minutos', minimo=5
    )

    resultado = banco.executar(
        'INSERT INTO procedimentos (nome, descricao, preco, duracao_minutos) '
        'VALUES (%s, %s, %s, %s)',
        (nome, descricao, preco, duracao),
    )
    return jsonify({
        'mensagem': 'Procedimento criado com sucesso.',
        'dados': {'id': resultado['ultimo_id']},
    }), 201


@bp.put('/api/procedimentos/<int:registro_id>')
def atualizar_procedimento(registro_id):
    """Edita um procedimento (pode enviar so os campos que mudaram)."""
    if not banco.consultar_um(
        'SELECT id FROM procedimentos WHERE id = %s', (registro_id,)
    ):
        return resposta_erro('Procedimento nao encontrado.', 404)

    dados = request.get_json(silent=True)
    exigir_json(dados)

    campos = {}
    if 'nome' in dados:
        campos['nome'] = texto(dados, 'nome', 80)
    if 'descricao' in dados:
        campos['descricao'] = texto(dados, 'descricao', 200,
                                    obrigatorio=False)
    if 'preco' in dados:
        campos['preco'] = validar_preco(dados['preco'])
    if 'duracao_minutos' in dados:
        campos['duracao_minutos'] = validar_inteiro(
            dados['duracao_minutos'], 'duracao_minutos', minimo=5
        )

    if not campos:
        raise ErroValidacao('Informe ao menos um campo para atualizar.')

    sql = ('UPDATE procedimentos SET '
           + ', '.join(f'{nome_campo} = %s' for nome_campo in campos)
           + ' WHERE id = %s')
    banco.executar(sql, (*campos.values(), registro_id))

    atualizado = banco.consultar_um(
        f'SELECT {CAMPOS} FROM procedimentos WHERE id = %s', (registro_id,)
    )
    return jsonify({
        'mensagem': 'Procedimento atualizado com sucesso.',
        'dados': atualizado,
    })


@bp.delete('/api/procedimentos/<int:registro_id>')
def excluir_procedimento(registro_id):
    """Exclui um procedimento. Se houver consultas vinculadas, o MySQL
    bloqueia (ON DELETE RESTRICT) e a API responde 409."""
    resultado = banco.executar(
        'DELETE FROM procedimentos WHERE id = %s', (registro_id,)
    )
    if resultado['linhas_afetadas'] == 0:
        return resposta_erro('Procedimento nao encontrado.', 404)
    return jsonify({'mensagem': 'Procedimento excluido com sucesso.'})
