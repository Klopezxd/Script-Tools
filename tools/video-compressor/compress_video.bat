@echo off
title Video Compressor (Multi-Codec & Hardware-Accelerated)
chcp 65001 >nul

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python no está disponible en el PATH del sistema.
    echo Instala Python 3.10+ para ejecutar el compresor de video.
    echo.
    pause
    exit /b 1
)

python "%~dp0compress_video.py" %*

echo.
pause
