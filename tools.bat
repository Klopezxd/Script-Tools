@echo off
setlocal
title Script-Tools Suite
chcp 65001 >nul

where python >nul 2>nul
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
    python "%~dp0tools.py" menu
) else (
    python "%~dp0tools.py" %*
)
if %ERRORLEVEL% neq 0 (
    echo.
    echo [AVISO] La ejecución finalizó con código de salida %ERRORLEVEL%.
    pause
)
