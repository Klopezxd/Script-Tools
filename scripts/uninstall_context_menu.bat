@echo off
title Script-Tools - Desinstalar Menu Contextual
chcp 65001 >nul

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0uninstall_context_menu.ps1"

echo.
pause
