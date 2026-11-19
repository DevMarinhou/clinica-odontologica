"""CRUD de dentistas (profissionais da clinica)."""
from flask import Blueprint, jsonify, request

from app import banco
from app.erros import resposta_erro
from app.validacao import (
    ErroValidacao,
    exigir_campos,
    exigir_json,
    texto,
    validar_ativo,
    validar_email,
)

bp = Blueprint('dentistas', __name__)

CAMPOS = 'id, nome, cro, especialidade, telefone, email, ativo, criado_em'


@bp.get('/api/dentistas')
def listar_dentistas():
    """Lista dentistas. Aceita ?busca=xxx (nome, CRO, especialidade)."""
    busca = (request.args.get('busca') or '').strip()
    sql = f'SELECT {CAMPOS} FROM dentistas'
    params = []
    if busca:
        sql += (' WHERE nome LIKE %s OR cro LIKE %s '
                'OR especialidade LIKE %s OR email LIKE %s')
        like = f'%{busca}%'
        params.extend([like, like, like, like])
    sql += ' ORDER BY nome ASC'
    linhas = banco.consultar(sql, params)
    return jsonify({'total': len(linhas), 'dados': linhas})


@bp.get('/api/dentistas/<int:registro_id>')
def buscar_dentista(registro_id):
    """Busca um dentista pelo id."""
    linha = banco.consultar_um(
        f'SELECT {CAMPOS} FROM dentistas WHERE id = %s', (registro_id,)
    )
    if not linha:
        return resposta_erro('Dentista nao encontrado.', 404)
    return jsonify({'dados': linha})


@bp.post('/api/dentistas')
def criar_dentista():
    """Cadastra um novo dentista."""
    dados = request.get_json(silent=True)
    exigir_campos(dados, ['nome', 'cro'])

    nome = texto(dados, 'nome', 100)
    cro = texto(dados, 'cro', 20)
    especialidade = texto(dados, 'especialidade', 60, obrigatorio=False)
    telefone = texto(dados, 'telefone', 20, obrigatorio=False)
    email = validar_email(dados.get('email'))
    ativo = validar_ativo(dados.get('ativo'))

    resultado = banco.executar(
        'INSERT INTO dentistas (nome, cro, especialidade, telefone, email, ativo) '
        'VALUES (%s, %s, %s, %s, %s, %s)',
        (nome, cro, especialidade, telefone, email, ativo),
    )
    return jsonify({
        'mensagem': 'Dentista criado com sucesso.',
        'dados': {'id': resultado['ultimo_id']},
    }), 201


@bp.put('/api/dentistas/<int:registro_id>')
def atualizar_dentista(registro_id):
    """Edita um dentista (pode enviar so os campos que mudaram)."""
    if not banco.consultar_um(
        'SELECT id FROM dentistas WHERE id = %s', (registro_id,)
    ):
        return resposta_erro('Dentista nao encontrado.', 404)

    dados = request.get_json(silent=True)
    exigir_json(dados)

    campos = {}
    if 'nome' in dados:
        campos['nome'] = texto(dados, 'nome', 100)
    if 'cro' in dados:
        campos['cro'] = texto(dados, 'cro', 20)
    if 'especialidade' in dados:
        campos['especialidade'] = texto(dados, 'especialidade', 60,
                                        obrigatorio=False)
    if 'telefone' in dados:
        campos['telefone'] = texto(dados, 'telefone', 20, obrigatorio=False)
    if 'email' in dados:
        campos['email'] = validar_email(dados.get('email'))
    if 'ativo' in dados:
        campos['ativo'] = validar_ativo(dados['ativo'])

    if not campos:
        raise ErroValidacao('Informe ao menos um campo para atualizar.')

    sql = ('UPDATE dentistas SET '
           + ', '.join(f'{nome_campo} = %s' for nome_campo in campos)
           + ' WHERE id = %s')
    banco.executar(sql, (*campos.values(), registro_id))

    atualizado = banco.consultar_um(
        f'SELECT {CAMPOS} FROM dentistas WHERE id = %s', (registro_id,)
    )
    return jsonify({
        'mensagem': 'Dentista atualizado com sucesso.',
        'dados': atualizado,
    })


@bp.delete('/api/dentistas/<int:registro_id>')
def excluir_dentista(registro_id):
    """Exclui um dentista. Se houver consultas vinculadas, o MySQL
    bloqueia (ON DELETE RESTRICT) e a API responde 409."""
    resultado = banco.executar(
        'DELETE FROM dentistas WHERE id = %s', (registro_id,)
    )
    if resultado['linhas_afetadas'] == 0:
        return resposta_erro('Dentista nao encontrado.', 404)
    return jsonify({'mensagem': 'Dentista excluido com sucesso.'})
