@echo off
title Script-Tools - Instalar Menu Contextual
chcp 65001 >nul

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_context_menu.ps1"

echo.
pause
