@echo off
title Setup Script-Tools
chcp 65001 >nul

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"

echo.
pause
