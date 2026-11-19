"""Camada de acesso ao banco de dados MySQL.

Aqui mora TODO o SQL da aplicacao (SELECT, INSERT, UPDATE, DELETE).
Usamos SQL puro de proposito: a atividade exige demonstrar o uso
desses comandos, e deixar o SQL explicito facilita explica-lo na
apresentacao.

As conexoes sao gerenciadas por um POOL (fila de conexoes prontas),
que e mais rapido do que abrir uma conexao nova a cada requisicao.
"""
import datetime
import decimal

import mysql.connector
from mysql.connector import pooling

_pool = None


def iniciar_pool(app):
    """Cria o pool de conexoes a partir da configuracao da app."""
    global _pool
    _pool = pooling.MySQLConnectionPool(
        pool_name='pool_clinica',
        pool_size=int(app.config.get('POOL_SIZE', 5)),
        host=app.config['MYSQL_HOST'],
        port=int(app.config['MYSQL_PORT']),
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DATABASE'],
        charset='utf8mb4',
        use_pure=True,
    )


def _obter_conexao():
    if _pool is None:
        raise RuntimeError('Pool de conexoes nao iniciado. Chame iniciar_pool().')
    return _pool.get_connection()


def _serializar(valor):
    """Converte tipos do MySQL em tipos aceitos pelo JSON."""
    if isinstance(valor, datetime.datetime):
        return valor.isoformat()          # 2026-11-19T15:30:00
    if isinstance(valor, datetime.date):
        return valor.isoformat()          # 1990-05-12
    if isinstance(valor, decimal.Decimal):
        return float(valor)               # 150.00 -> 150.0
    if isinstance(valor, datetime.timedelta):
        return str(valor)
    if isinstance(valor, (bytes, bytearray)):
        return valor.decode('utf-8', 'replace')
    return valor


def _serializar_linha(linha):
    return {chave: _serializar(valor) for chave, valor in linha.items()}


def consultar(sql, params=()):
    """Executa um SELECT e devolve a lista de linhas (dicts)."""
    conexao = _obter_conexao()
    try:
        with conexao.cursor(dictionary=True) as cursor:
            cursor.execute(sql, params)
            return [_serializar_linha(l) for l in cursor.fetchall()]
    finally:
        conexao.close()   # devolve a conexao ao pool


def consultar_um(sql, params=()):
    """Executa um SELECT e devolve a primeira linha ou None."""
    linhas = consultar(sql, params)
    return linhas[0] if linhas else None


def executar(sql, params=()):
    """Executa INSERT/UPDATE/DELETE com commit e rollback automatico.

    Devolve:
        {'linhas_afetadas': int, 'ultimo_id': int|None}
    """
    conexao = _obter_conexao()
    try:
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, params)
            conexao.commit()
            return {
                'linhas_afetadas': cursor.rowcount,
                'ultimo_id': cursor.lastrowid,
            }
        except Exception:
            conexao.rollback()   # desfaz tudo se algo falhar no meio
            raise
        finally:
            cursor.close()
    finally:
        conexao.close()          # devolve a conexao ao pool
