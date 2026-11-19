"""CRUD de consultas - o coracao do sistema.

A listagem usa JOIN nas 3 tabelas (pacientes, dentistas e
procedimentos) para devolver tudo pronto para a tela exibir:

    GET /api/consultas
    -> SELECT c.*, p.nome, d.nome, pr.nome
       FROM consultas c
       JOIN pacientes p     ON p.id = c.paciente_id
       JOIN dentistas d     ON d.id = c.dentista_id
       JOIN procedimentos pr ON pr.id = c.procedimento_id
"""
from flask import Blueprint, jsonify, request

from app import banco
from app.erros import resposta_erro
from app.validacao import (
    ErroValidacao,
    exigir_campos,
    exigir_json,
    texto,
    validar_data,
    validar_data_hora,
    validar_inteiro,
    validar_status,
)

bp = Blueprint('consultas', __name__)

_TABELAS_PERMITIDAS = ('pacientes', 'dentistas', 'procedimentos')

_SELECT_CONSULTA = """
SELECT c.id, c.data_hora, c.status, c.observacoes, c.criado_em,
       c.paciente_id,      p.nome  AS paciente_nome,      p.cpf   AS paciente_cpf,
       c.dentista_id,      d.nome  AS dentista_nome,      d.cro   AS dentista_cro,
       c.procedimento_id,  pr.nome AS procedimento_nome,  pr.preco AS procedimento_preco,
       pr.duracao_minutos  AS procedimento_duracao_minutos
FROM consultas c
JOIN pacientes p      ON p.id = c.paciente_id
JOIN dentistas d      ON d.id = c.dentista_id
JOIN procedimentos pr ON pr.id = c.procedimento_id
"""


def _exigir_registro(tabela, registro_id, rotulo):
    """Confere se o id existe antes de gravar (mensagem mais amigavel
    do que o erro cru de chave estrangeira)."""
    if tabela not in _TABELAS_PERMITIDAS:
        raise ErroValidacao('Tabela nao permitida.')
    if not banco.consultar_um(
        f'SELECT id FROM {tabela} WHERE id = %s', (registro_id,)
    ):
        raise ErroValidacao(f'{rotulo} nao encontrado (id {registro_id}).')


@bp.get('/api/consultas')
def listar_consultas():
    """Lista consultas com JOIN. Filtros opcionais:
    ?busca=, ?status=, ?data=AAAA-MM-DD, ?paciente_id=, ?dentista_id=
    """
    clausulas = []
    params = []

    busca = (request.args.get('busca') or '').strip()
    if busca:
        clausulas.append('(p.nome LIKE %s OR c.observacoes LIKE %s '
                         'OR pr.nome LIKE %s)')
        like = f'%{busca}%'
        params.extend([like, like, like])

    status = validar_status(request.args.get('status'))
    if status:
        clausulas.append('c.status = %s')
        params.append(status)

    data = (request.args.get('data') or '').strip()
    if data:
        clausulas.append('DATE(c.data_hora) = %s')
        params.append(validar_data(data))

    if request.args.get('paciente_id'):
        paciente_id = validar_inteiro(
            request.args['paciente_id'], 'paciente_id', minimo=1
        )
        clausulas.append('c.paciente_id = %s')
        params.append(paciente_id)

    if request.args.get('dentista_id'):
        dentista_id = validar_inteiro(
            request.args['dentista_id'], 'dentista_id', minimo=1
        )
        clausulas.append('c.dentista_id = %s')
        params.append(dentista_id)

    sql = _SELECT_CONSULTA
    if clausulas:
        sql += ' WHERE ' + ' AND '.join(clausulas)
    sql += ' ORDER BY c.data_hora DESC'

    linhas = banco.consultar(sql, params)
    return jsonify({'total': len(linhas), 'dados': linhas})


@bp.get('/api/consultas/<int:registro_id>')
def buscar_consulta(registro_id):
    """Busca uma consulta pelo id, ja com os dados das 3 tabelas."""
    linha = banco.consultar_um(
        _SELECT_CONSULTA + ' WHERE c.id = %s', (registro_id,)
    )
    if not linha:
        return resposta_erro('Consulta nao encontrada.', 404)
    return jsonify({'dados': linha})


@bp.post('/api/consultas')
def criar_consulta():
    """Agenda uma nova consulta."""
    dados = request.get_json(silent=True)
    exigir_campos(dados,
                  ['paciente_id', 'dentista_id', 'procedimento_id',
                   'data_hora'])

    paciente_id = validar_inteiro(dados['paciente_id'], 'paciente_id', 1)
    dentista_id = validar_inteiro(dados['dentista_id'], 'dentista_id', 1)
    procedimento_id = validar_inteiro(dados['procedimento_id'],
                                      'procedimento_id', 1)
    data_hora = validar_data_hora(dados['data_hora'])
    status = validar_status(dados.get('status')) or 'agendada'
    observacoes = texto(dados, 'observacoes', 255, obrigatorio=False)

    # Verifica as chaves estrangeiras antes de inserir
    _exigir_registro('pacientes', paciente_id, 'Paciente')
    _exigir_registro('dentistas', dentista_id, 'Dentista')
    _exigir_registro('procedimentos', procedimento_id, 'Procedimento')

    resultado = banco.executar(
        'INSERT INTO consultas '
        '(paciente_id, dentista_id, procedimento_id, data_hora, status, '
        'observacoes) VALUES (%s, %s, %s, %s, %s, %s)',
        (paciente_id, dentista_id, procedimento_id, data_hora,
         status, observacoes),
    )
    return jsonify({
        'mensagem': 'Consulta agendada com sucesso.',
        'dados': {'id': resultado['ultimo_id']},
    }), 201


@bp.put('/api/consultas/<int:registro_id>')
def atualizar_consulta(registro_id):
    """Edita uma consulta (remarcar, mudar status, trocar dentista...)."""
    if not banco.consultar_um(
        'SELECT id FROM consultas WHERE id = %s', (registro_id,)
    ):
        return resposta_erro('Consulta nao encontrada.', 404)

    dados = request.get_json(silent=True)
    exigir_json(dados)

    campos = {}
    if 'paciente_id' in dados:
        paciente_id = validar_inteiro(dados['paciente_id'], 'paciente_id', 1)
        _exigir_registro('pacientes', paciente_id, 'Paciente')
        campos['paciente_id'] = paciente_id
    if 'dentista_id' in dados:
        dentista_id = validar_inteiro(dados['dentista_id'], 'dentista_id', 1)
        _exigir_registro('dentistas', dentista_id, 'Dentista')
        campos['dentista_id'] = dentista_id
    if 'procedimento_id' in dados:
        procedimento_id = validar_inteiro(dados['procedimento_id'],
                                          'procedimento_id', 1)
        _exigir_registro('procedimentos', procedimento_id, 'Procedimento')
        campos['procedimento_id'] = procedimento_id
    if 'data_hora' in dados:
        campos['data_hora'] = validar_data_hora(dados['data_hora'])
    if 'status' in dados:
        campos['status'] = validar_status(dados['status'], obrigatorio=True)
    if 'observacoes' in dados:
        campos['observacoes'] = texto(dados, 'observacoes', 255,
                                      obrigatorio=False)

    if not campos:
        raise ErroValidacao('Informe ao menos um campo para atualizar.')

    sql = ('UPDATE consultas SET '
           + ', '.join(f'{nome_campo} = %s' for nome_campo in campos)
           + ' WHERE id = %s')
    banco.executar(sql, (*campos.values(), registro_id))

    atualizada = banco.consultar_um(
        _SELECT_CONSULTA + ' WHERE c.id = %s', (registro_id,)
    )
    return jsonify({
        'mensagem': 'Consulta atualizada com sucesso.',
        'dados': atualizada,
    })


@bp.delete('/api/consultas/<int:registro_id>')
def excluir_consulta(registro_id):
    """Cancela/exclui uma consulta do sistema."""
    resultado = banco.executar(
        'DELETE FROM consultas WHERE id = %s', (registro_id,)
    )
    if resultado['linhas_afetadas'] == 0:
        return resposta_erro('Consulta nao encontrada.', 404)
    return jsonify({'mensagem': 'Consulta excluida com sucesso.'})
