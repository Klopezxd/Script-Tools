@echo off
title PDF Optimizer (Multi-Engine & OCR-Safe)
chcp 65001 >nul

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python no está disponible en el PATH del sistema.
    echo Instala Python 3.10+ y las dependencias para ejecutar el optimizador de PDF.
    echo.
    pause
    exit /b 1
)

python "%~dp0pdf_optimizer.py" %*

echo.
pause
