"""Configuracao da aplicacao lida do arquivo .env."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Carrega o .env da RAIZ do projeto, independentemente de onde o
# python foi executado (raiz do projeto, subpasta, IDE, etc.)
load_dotenv(Path(__file__).resolve().parent.parent / '.env')


class Config:
    """Configuracoes padrao da API."""

    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
    MYSQL_USER = os.getenv('MYSQL_USER', 'clinica_app')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'clinica_odontologica')

    PORTA = int(os.getenv('PORTA', '5000'))
    DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'
    POOL_SIZE = int(os.getenv('POOL_SIZE', '5'))
