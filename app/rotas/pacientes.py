"""CRUD de pacientes (listar, buscar, criar, editar, excluir).

Cada rota abaixo e um comando SQL diferente:
  GET    -> SELECT
  POST   -> INSERT
  PUT    -> UPDATE
  DELETE -> DELETE
"""
from flask import Blueprint, jsonify, request

from app import banco
from app.erros import resposta_erro
from app.validacao import (
    ErroValidacao,
    exigir_campos,
    exigir_json,
    texto,
    validar_cpf,
    validar_data,
    validar_email,
)

bp = Blueprint('pacientes', __name__)

# Campos devolvidos ao cliente (sem nada sutil)
CAMPOS = 'id, nome, cpf, data_nascimento, telefone, email, endereco, criado_em'


@bp.get('/api/pacientes')
def listar_pacientes():
    """Lista pacientes. Aceita ?busca=xxx para pesquisar."""
    busca = (request.args.get('busca') or '').strip()
    sql = f'SELECT {CAMPOS} FROM pacientes'
    params = []
    if busca:
        sql += (' WHERE nome LIKE %s OR cpf LIKE %s '
                'OR email LIKE %s OR telefone LIKE %s')
        like = f'%{busca}%'
        params.extend([like, like, like, like])
    sql += ' ORDER BY nome ASC'
    linhas = banco.consultar(sql, params)
    return jsonify({'total': len(linhas), 'dados': linhas})


@bp.get('/api/pacientes/<int:registro_id>')
def buscar_paciente(registro_id):
    """Busca um paciente pelo id."""
    linha = banco.consultar_um(
        f'SELECT {CAMPOS} FROM pacientes WHERE id = %s', (registro_id,)
    )
    if not linha:
        return resposta_erro('Paciente nao encontrado.', 404)
    return jsonify({'dados': linha})


@bp.post('/api/pacientes')
def criar_paciente():
    """Cadastra um novo paciente."""
    dados = request.get_json(silent=True)
    exigir_campos(dados, ['nome', 'cpf', 'data_nascimento'])

    nome = texto(dados, 'nome', 100)
    cpf = validar_cpf(dados['cpf'])
    data_nascimento = validar_data(dados['data_nascimento'])
    telefone = texto(dados, 'telefone', 20, obrigatorio=False)
    email = validar_email(dados.get('email'))
    endereco = texto(dados, 'endereco', 150, obrigatorio=False)

    resultado = banco.executar(
        'INSERT INTO pacientes '
        '(nome, cpf, data_nascimento, telefone, email, endereco) '
        'VALUES (%s, %s, %s, %s, %s, %s)',
        (nome, cpf, data_nascimento, telefone, email, endereco),
    )
    return jsonify({
        'mensagem': 'Paciente criado com sucesso.',
        'dados': {'id': resultado['ultimo_id']},
    }), 201


@bp.put('/api/pacientes/<int:registro_id>')
def atualizar_paciente(registro_id):
    """Edita um paciente (pode enviar so os campos que mudaram)."""
    if not banco.consultar_um(
        'SELECT id FROM pacientes WHERE id = %s', (registro_id,)
    ):
        return resposta_erro('Paciente nao encontrado.', 404)

    dados = request.get_json(silent=True)
    exigir_json(dados)

    campos = {}
    if 'nome' in dados:
        campos['nome'] = texto(dados, 'nome', 100)
    if 'cpf' in dados:
        campos['cpf'] = validar_cpf(dados['cpf'])
    if 'data_nascimento' in dados:
        campos['data_nascimento'] = validar_data(dados['data_nascimento'])
    if 'telefone' in dados:
        campos['telefone'] = texto(dados, 'telefone', 20, obrigatorio=False)
    if 'email' in dados:
        campos['email'] = validar_email(dados.get('email'))
    if 'endereco' in dados:
        campos['endereco'] = texto(dados, 'endereco', 150, obrigatorio=False)

    if not campos:
        raise ErroValidacao('Informe ao menos um campo para atualizar.')

    sql = ('UPDATE pacientes SET '
           + ', '.join(f'{nome_campo} = %s' for nome_campo in campos)
           + ' WHERE id = %s')
    banco.executar(sql, (*campos.values(), registro_id))

    atualizado = banco.consultar_um(
        f'SELECT {CAMPOS} FROM pacientes WHERE id = %s', (registro_id,)
    )
    return jsonify({
        'mensagem': 'Paciente atualizado com sucesso.',
        'dados': atualizado,
    })


@bp.delete('/api/pacientes/<int:registro_id>')
def excluir_paciente(registro_id):
    """Exclui um paciente. Se houver consultas vinculadas, o MySQL
    bloqueia (ON DELETE RESTRICT) e a API responde 409."""
    resultado = banco.executar(
        'DELETE FROM pacientes WHERE id = %s', (registro_id,)
    )
    if resultado['linhas_afetadas'] == 0:
        return resposta_erro('Paciente nao encontrado.', 404)
    return jsonify({'mensagem': 'Paciente excluido com sucesso.'})
