@echo off
title Compresor de Video H.265
chcp 65001 >nul

if "%~1"=="" (
    echo [INFO] No arrastraste un archivo. Abriendo selector interactivo...
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0compress_video.ps1"
) else (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0compress_video.ps1" -InputFile "%~1"
)

echo.
pause
