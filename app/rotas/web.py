"""Servidor das paginas do Front-end.

O front-end e estatico (HTML + CSS + Bootstrap + JavaScript puro) e
fica na pasta `front-end/`. O Flask serve esses arquivos, de modo que
a aplicacao COMPLETA (telas + API) funciona em um unico endereco:

    http://127.0.0.1:5000

As rotas /api/... continuam prioritarias: regras estaticas do
Flask tem precedencia sobre a regra dinamica deste blueprint.
"""
from pathlib import Path

from flask import Blueprint, abort, send_from_directory

# app/rotas/web.py -> app/rotas -> app -> raiz do projeto -> front-end
PASTA_FRONT_END = Path(__file__).resolve().parents[2] / 'front-end'

bp = Blueprint('web', __name__)


@bp.get('/')
def pagina_inicial():
    """Tela inicial: login e painel principal."""
    return send_from_directory(PASTA_FRONT_END, 'index.html')


@bp.get('/<path:arquivo>')
def arquivos_do_front_end(arquivo):
    """Serve os arquivos estaticos do front-end (HTML, CSS, JS, fontes)."""
    raiz = PASTA_FRONT_END.resolve()
    destino = (raiz / arquivo).resolve()

    # protecao contra "path traversal" (ex.: ../../etc/passwd)
    if destino != raiz and raiz not in destino.parents:
        abort(404)

    if not destino.is_file():
        abort(404)

    return send_from_directory(PASTA_FRONT_END, arquivo)
