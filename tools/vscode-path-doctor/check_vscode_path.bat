@echo off
title VS Code PATH Doctor
chcp 65001 >nul

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0check_vscode_path.ps1"

echo.
pause
