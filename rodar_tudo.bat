@echo off
cd /d "%~dp0"
echo ================================================
echo  Teste Tecnico - Luis Gustavo Corsino
echo ================================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    where py >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERRO: Python nao encontrado no PATH.
        echo Instale Python 3.9+ e marque "Add to PATH" na instalacao.
        pause
        exit /b 1
    )
    set PYTHON=py
) else (
    set PYTHON=python
)

echo Verificando dependencias Python...
%PYTHON% -m pip install --quiet pandas pyarrow duckdb matplotlib
echo Dependencias OK.
echo.

echo [1/3] Gerando ETL + EDA + slides PDF (Q4)...
%PYTHON% Q4_analise.py
echo.

echo [2/3] Gerando dashboard NPS estatico (Q2)...
%PYTHON% Q2_dashboard.py
echo.

echo [3/3] Executando queries SQL (Q3)...
%PYTHON% Q3_queries.py
echo.

echo ================================================
echo  Concluido! Arquivos em:
echo  %USERPROFILE%\Desktop\Teste Tecnico - Luis Gustavo\
echo ================================================
pause
