@echo off
echo ========================================================
echo Iniciando Servidor Local da Aplicacao de Mineracao de Dados
echo ========================================================
echo Abrindo em http://localhost:8000
echo Swagger UI disponivel em http://localhost:8000/docs
echo Pressione Ctrl+C para encerrar.
echo ========================================================
py -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
pause
