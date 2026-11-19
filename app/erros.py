"""Tratamento centralizado de erros da API.

Regra de ouro da API: TODA resposta de erro sai no mesmo formato:
    {"erro": "mensagem clara em portugues"}
com o codigo HTTP adequado (400, 401, 404, 409, 500, 503...).
Assim o front-end so precisa checar 'corpo.erro' para exibir o aviso.
"""
from flask import jsonify
from mysql.connector import Error as ErroMySQL
from mysql.connector.errors import IntegrityError, InterfaceError, OperationalError


def resposta_erro(mensagem, status=400, **extras):
    """Monta a padrao de resposta de erro."""
    corpo = {'erro': mensagem}
    corpo.update(extras)
    return jsonify(corpo), status


def registrar_tratadores(app):
    """Registra todos os tratadores de erro na aplicacao."""

    # Imports locais evitam circulo de importacao
    from app.validacao import ErroValidacao

    @app.errorhandler(ErroValidacao)
    def _validacao(erro):
        return resposta_erro(str(erro), 400)

    @app.errorhandler(IntegrityError)
    def _integridade(erro):
        texto = str(erro).lower()
        if 'duplicate' in texto:
            return resposta_erro(
                'Ja existe um registro com esse valor unico '
                '(chave duplicada).', 409
            )
        if 'foreign key' in texto:
            return resposta_erro(
                'Operacao nao permitida: o registro esta vinculado '
                'a outros dados (integridade referencial).', 409
            )
        return resposta_erro('Violacao de integridade no banco de dados.', 409)

    @app.errorhandler(OperationalError)
    @app.errorhandler(InterfaceError)
    def _conexao(erro):
        return resposta_erro(
            'Nao foi possivel conectar ao banco de dados. '
            'Verifique se o servico MySQL84 esta ativo.', 503
        )

    @app.errorhandler(ErroMySQL)
    def _mysql(erro):
        app.logger.error('Erro MySQL: %s', erro)
        return resposta_erro('Erro no banco de dados.', 500)

    @app.errorhandler(404)
    def _nao_encontrado(erro):
        return resposta_erro(
            'Rota nao encontrada. Consulte docs/03-guia-integracao-front-end.md',
            404
        )

    @app.errorhandler(405)
    def _metodo_invalido(erro):
        return resposta_erro('Metodo HTTP nao permitido para esta rota.', 405)

    @app.errorhandler(Exception)
    def _inesperado(erro):
        app.logger.exception('Erro nao tratado: %s', erro)
        return resposta_erro('Erro interno inesperado.', 500)
