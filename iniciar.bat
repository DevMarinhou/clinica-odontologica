@echo off
title Clinica Odontologica - API Back-end
cd /d "%~dp0"

echo.
echo  ============================================
echo   Clinica Odontologica - API Back-end
echo   http://127.0.0.1:5000
echo.
echo   Antes de iniciar, certifique-se de que o
echo   servico do MySQL (MySQL84) esta ativo.
echo  ============================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo  [ERRO] Ambiente virtual nao encontrado.
    echo  Execute: python -m venv venv
    echo  Depois:  venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python run.py

pause
