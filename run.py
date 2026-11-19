"""Ponto de entrada da API - Clinica Odontologica.

Executar:
    python run.py
ou simplesmente dar duplo clique em iniciar.bat
"""
from app import create_app
from app.config import Config

app = create_app()

if __name__ == '__main__':
    print('=' * 60)
    print('  API Clinica Odontologica - Back-end')
    print(f'  http://127.0.0.1:{Config.PORTA}')
    print('  Banco: MySQL (clinica_odontologica)')
    print('=' * 60)
    app.run(host='127.0.0.1', port=Config.PORTA, debug=Config.DEBUG)
