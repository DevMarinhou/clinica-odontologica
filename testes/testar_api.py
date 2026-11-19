"""Testes automatizados da API - Clinica Odontologica.

O que faz: percorre TODAS as operacoes CRUD de ponta a ponta,
checando status HTTP e conteudo das respostas.

Como usar:
    1) Inicie a API (python run.py ou iniciar.bat)
    2) Em outro terminal:
           venv\\Scripts\\python testes\\testar_api.py

Sai com codigo 0 se tudo passou, 1 se algo falhou.
"""
import json
import sys
import urllib.error
import urllib.request

BASE = 'http://127.0.0.1:5000'
falhas = []
passes = []


def requisitar(metodo, caminho, corpo=None, esperado=200):
    """Faz uma chamada HTTP e devolve (status, json_resposta)."""
    url = BASE + caminho
    dados = json.dumps(corpo).encode('utf-8') if corpo is not None else None
    cabecalhos = {'Content-Type': 'application/json'}
    req = urllib.request.Request(url, data=dados, headers=cabecalhos,
                                 method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=10) as resposta:
            status = resposta.status
            texto = resposta.read().decode('utf-8')
    except urllib.error.HTTPError as erro:
        status = erro.code
        texto = erro.read().decode('utf-8')
    except urllib.error.URLError as erro:
        return 0, {'erro': f'API offline: {erro.reason}'}

    try:
        conteudo = json.loads(texto) if texto else {}
    except json.JSONDecodeError:
        conteudo = {'_bruto': texto}
    return status, conteudo


def conferir(nome, condicao, detalhe=''):
    """Registra o resultado de uma verificacao."""
    if condicao:
        passes.append(nome)
        print(f'  [OK]   {nome}')
    else:
        falhas.append(f'{nome} {detalhe}')
        print(f'  [FALHA] {nome} {detalhe}')


def conferir_http(nome, status_obtido, esperado, conteudo):
    conferir(
        f'{nome} -> HTTP {esperado}',
        status_obtido == esperado,
        f'(obtido {status_obtido}: {json.dumps(conteudo, ensure_ascii=False)[:120]})',
    )


def main():
    print('=' * 70)
    print('  TESTES DA API - CLINICA ODONTOLOGICA')
    print(f'  Alvo: {BASE}')
    print('=' * 70)

    # ---------------------------------------------------------
    print('\n1) APLICACAO ONLINE')
    status, corpo = requisitar('GET', '/api/status')
    conferir_http('GET /api/status', status, 200, corpo)
    conferir('API responde "status: online"', corpo.get('status') == 'online')

    # ---------------------------------------------------------
    print('\n2) BANCO DE DADOS (>= 5 registros por tabela)')
    status, painel = requisitar('GET', '/api/painel/resumo')
    conferir_http('GET /api/painel/resumo', status, 200, painel)
    totais = painel.get('dados', {}).get('totais', {})
    for tabela in ('pacientes', 'dentistas', 'procedimentos',
                   'consultas', 'usuarios'):
        valor = totais.get(tabela, 0)
        conferir(f'{tabela}: {valor} registros (minimo 5)', valor >= 5)

    # ---------------------------------------------------------
    print('\n3) LISTAGEM E PESQUISA (SELECT + LIKE)')
    status, lista = requisitar('GET', '/api/pacientes')
    conferir_http('GET /api/pacientes', status, 200, lista)
    conferir('lista possui o campo total', 'total' in lista)

    status, busca = requisitar('GET', '/api/pacientes?busca=Maria')
    conferir_http('GET /api/pacientes?busca=Maria', status, 200, busca)
    conferir('pesquisa por nome encontra "Maria Silva"',
             any('Maria' in p.get('nome', '') for p in busca.get('dados', [])))

    status, por_status = requisitar('GET', '/api/consultas?status=agendada')
    conferir_http('GET /api/consultas?status=agendada', status, 200, por_status)
    conferir('filtro devolve so consultas agendadas',
             all(c.get('status') == 'agendada'
                 for c in por_status.get('dados', [])))

    # ---------------------------------------------------------
    print('\n4) JOIN ENTRE TABELAS (GET /api/consultas)')
    status, consultas = requisitar('GET', '/api/consultas')
    conferir_http('GET /api/consultas', status, 200, consultas)
    primeira = (consultas.get('dados') or [{}])[0]
    for campo in ('paciente_nome', 'dentista_nome', 'procedimento_nome',
                  'procedimento_preco'):
        conferir(f'JOIN devolve o campo {campo}', campo in primeira)

    # ---------------------------------------------------------
    print('\n5) CRUD DE PACIENTES (INSERT/SELECT/UPDATE/DELETE)')
    novo = {
        'nome': 'Paciente Dos Testes',
        'cpf': '529.982.247-25',          # CPF valido de exemplo
        'data_nascimento': '1988-12-30',
        'telefone': '(11) 90000-1234',
        'email': 'paciente.testes@email.com',
        'endereco': 'Rua dos Testes, 42',
    }
    status, criado = requisitar('POST', '/api/pacientes', novo)
    conferir_http('POST /api/pacientes (criar)', status, 201, criado)
    id_paciente = criado.get('dados', {}).get('id')

    status, buscado = requisitar('GET', f'/api/pacientes/{id_paciente}')
    conferir_http('GET /api/pacientes/<id>', status, 200, buscado)
    conferir('nome gravado corretamente',
             buscado.get('dados', {}).get('nome') == novo['nome'])
    conferir('data de nascimento no formato AAAA-MM-DD',
             buscado.get('dados', {}).get('data_nascimento') == '1988-12-30')

    status, editado = requisitar(
        'PUT', f'/api/pacientes/{id_paciente}',
        {'nome': 'Paciente Editado', 'telefone': '(11) 99999-0000'},
    )
    conferir_http('PUT /api/pacientes/<id> (editar)', status, 200, editado)
    conferir('edicao persistiu no banco',
             editado.get('dados', {}).get('nome') == 'Paciente Editado')

    status, excluido = requisitar('DELETE', f'/api/pacientes/{id_paciente}')
    conferir_http('DELETE /api/pacientes/<id>', status, 200, excluido)
    status, depois = requisitar('GET', f'/api/pacientes/{id_paciente}')
    conferir_http('registro excluido nao existe mais (404)',
                  status, 404, depois)

    # ---------------------------------------------------------
    print('\n6) CRUD DE DENTISTAS')
    novo_dentista = {'nome': 'Dentista Dos Testes', 'cro': 'CRO-SP 99999',
                     'especialidade': 'Testes'}
    status, criado = requisitar('POST', '/api/dentistas', novo_dentista)
    conferir_http('POST /api/dentistas (criar)', status, 201, criado)
    id_dentista = criado.get('dados', {}).get('id')
    status, editado = requisitar('PUT', f'/api/dentistas/{id_dentista}',
                                 {'especialidade': 'Testes Editados'})
    conferir_http('PUT /api/dentistas/<id> (editar)', status, 200, editado)
    status, excluido = requisitar('DELETE', f'/api/dentistas/{id_dentista}')
    conferir_http('DELETE /api/dentistas/<id>', status, 200, excluido)

    # ---------------------------------------------------------
    print('\n7) CRUD DE PROCEDIMENTOS')
    novo_proc = {'nome': 'Procedimento Dos Testes', 'preco': '99,90',
                 'duracao_minutos': 15}
    status, criado = requisitar('POST', '/api/procedimentos', novo_proc)
    conferir_http('POST /api/procedimentos (criar)', status, 201, criado)
    id_proc = criado.get('dados', {}).get('id')
    status, editado = requisitar('PUT', f'/api/procedimentos/{id_proc}',
                                 {'preco': 120.50})
    conferir_http('PUT /api/procedimentos/<id> (editar)', status, 200, editado)
    conferir('preco aceitou virgula e ponto',
             editado.get('dados', {}).get('preco') in (120.5, '120.5'))
    status, excluido = requisitar('DELETE', f'/api/procedimentos/{id_proc}')
    conferir_http('DELETE /api/procedimentos/<id>', status, 200, excluido)

    # ---------------------------------------------------------
    print('\n8) CRUD DE CONSULTAS (com JOIN na resposta)')
    # Usa os ids 1 (paciente), 1 (dentista) e 1 (procedimento) dos seeds
    nova_consulta = {
        'paciente_id': 1, 'dentista_id': 1, 'procedimento_id': 1,
        'data_hora': '2026-12-24 10:00', 'status': 'agendada',
        'observacoes': 'Consulta criada pelos testes',
    }
    status, criado = requisitar('POST', '/api/consultas', nova_consulta)
    conferir_http('POST /api/consultas (criar)', status, 201, criado)
    id_consulta = criado.get('dados', {}).get('id')

    status, buscada = requisitar('GET', f'/api/consultas/{id_consulta}')
    conferir_http('GET /api/consultas/<id>', status, 200, buscada)
    conferir('GET individual traz o JOIN completo',
             'paciente_nome' in buscada.get('dados', {})
             and 'dentista_nome' in buscada.get('dados', {}))

    status, editada = requisitar(
        'PUT', f'/api/consultas/{id_consulta}', {'status': 'confirmada'})
    conferir_http('PUT /api/consultas/<id> (mudar status)', status, 200,
                  editada)
    conferir('status alterado para confirmada',
             editada.get('dados', {}).get('status') == 'confirmada')

    status, excluida = requisitar('DELETE', f'/api/consultas/{id_consulta}')
    conferir_http('DELETE /api/consultas/<id>', status, 200, excluida)

    # ---------------------------------------------------------
    print('\n9) USUARIOS E LOGIN (senha em hash)')
    status, lista_usuarios = requisitar('GET', '/api/usuarios')
    conferir_http('GET /api/usuarios', status, 200, lista_usuarios)
    conferir('resposta de usuarios NAO contem a senha',
             all('senha' not in u for u in lista_usuarios.get('dados', [])))

    status, login = requisitar('POST', '/api/auth/login',
                               {'nome_usuario': 'admin', 'senha': 'senha123'})
    conferir_http('POST /api/auth/login (senha correta)', status, 200, login)

    status, login_errado = requisitar(
        'POST', '/api/auth/login',
        {'nome_usuario': 'admin', 'senha': 'senha-errada'})
    conferir_http('POST /api/auth/login (senha errada -> 401)',
                  status, 401, login_errado)

    novo_usuario = {'nome_usuario': 'teste.usuario', 'senha': 'senha123',
                    'nome_completo': 'Usuario Dos Testes',
                    'perfil': 'recepcao'}
    status, criado = requisitar('POST', '/api/usuarios', novo_usuario)
    conferir_http('POST /api/usuarios (criar)', status, 201, criado)
    id_usuario = criado.get('dados', {}).get('id')
    status, editado = requisitar('PUT', f'/api/usuarios/{id_usuario}',
                                 {'perfil': 'admin'})
    conferir_http('PUT /api/usuarios/<id> (editar)', status, 200, editado)
    status, login_novo = requisitar(
        'POST', '/api/auth/login',
        {'nome_usuario': 'teste.usuario', 'senha': 'senha123'})
    conferir_http('usuario recem-criado consegue logar', status, 200,
                  login_novo)
    status, excluido = requisitar('DELETE', f'/api/usuarios/{id_usuario}')
    conferir_http('DELETE /api/usuarios/<id>', status, 200, excluido)

    # ---------------------------------------------------------
    print('\n10) VALIDACAO E ERROS ESPERADOS')
    status, erro_cpf = requisitar(
        'POST', '/api/pacientes',
        {'nome': 'X', 'cpf': '111.111.111-11', 'data_nascimento': '1990-01-01'})
    conferir_http('CPF invalido -> 400', status, 400, erro_cpf)
    conferir('erro no formato {"erro": mensagem}', 'erro' in erro_cpf)

    status, erro_404 = requisitar('GET', '/api/pacientes/99999')
    conferir_http('id inexistente -> 404', status, 404, erro_404)

    status, erro_dup = requisitar(
        'POST', '/api/pacientes',
        {'nome': 'Duplicado', 'cpf': '123.456.789-09',
         'data_nascimento': '1990-01-01'})
    conferir_http('CPF duplicado -> 409', status, 409, erro_dup)

    status, erro_fk = requisitar('DELETE', '/api/pacientes/1')
    conferir_http('excluir paciente com consultas -> 409 (FK RESTRICT)',
                  status, 409, erro_fk)

    status, erro_rota = requisitar('GET', '/api/rota-que-nao-existe')
    conferir_http('rota inexistente -> 404', status, 404, erro_rota)

    status, erro_status = requisitar('GET', '/api/consultas?status=inventado')
    conferir_http('status invalido no filtro -> 400', status, 400,
                  erro_status)

    # ---------------------------------------------------------
    print('\n' + '=' * 70)
    print(f'  RESULTADO: {len(passes)} passed, {len(falhas)} failed')
    print('=' * 70)
    if falhas:
        print('\nFALHAS:')
        for falha in falhas:
            print(f'  - {falha}')
        return 1
    print('\nTODOS OS TESTES PASSARAM! \\o/')
    return 0


if __name__ == '__main__':
    sys.exit(main())
