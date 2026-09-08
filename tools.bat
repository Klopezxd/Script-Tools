@echo off
setlocal
title Script-Tools Suite
chcp 65001 >nul

if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_CMD=%~dp0.venv\Scripts\python.exe"
) else (
    set "PYTHON_CMD=python"
)

%PYTHON_CMD% --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo.
    echo ========================================================
    echo  [ERROR] Python no está disponible en el PATH del sistema.
    echo ========================================================
    echo  Por favor instala Python 3.10 o superior y asegúrate de
    echo  marcar la casilla 'Add Python to PATH'.
    echo ========================================================
    echo.
    pause
    exit /b 1
)

if "%~1"=="" (
    "%PYTHON_CMD%" "%~dp0tools.py" menu
) else (
    "%PYTHON_CMD%" "%~dp0tools.py" %*
)
if %ERRORLEVEL% neq 0 (
    echo.
    echo [AVISO] La ejecución finalizó con código de salida %ERRORLEVEL%.
    pause
)
