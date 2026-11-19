"""Registro de todas as rotas da API (Blueprints)."""


def registrar_blueprints(app):
    """Registra todos os modulos de rota na aplicacao."""
    from app.rotas import (
        auth,
        consultas,
        dentistas,
        painel,
        pacientes,
        procedimentos,
        usuarios,
        web,
    )

    # a API entra primeiro; o blueprint 'web' (front-end) por ultimo
    for modulo in (auth, painel, pacientes, dentistas,
                   procedimentos, consultas, usuarios, web):
        app.register_blueprint(modulo.bp)
