@echo off
chcp 65001 >nul
REM =================================================================
REM  RESPALDO COMPLETO PRE-FORMATEO
REM  Ejecutor principal que llama al script de PowerShell
REM =================================================================

title Respaldo Completo Pre-Formateo
color 0A
cls

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                 RESPALDO COMPLETO PRE-FORMATEO               ║
echo  ║                                                              ║
echo  ║  Este script hara un respaldo completo de tu configuracion   ║
echo  ║  antes de formatear tu PC                                    ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

REM Verificar si el archivo PowerShell existe
if not exist "%~dp0backup_preformat.ps1" (
    echo [ERROR] No se encuentra el archivo backup_preformat.ps1
    echo.
    echo    El archivo debe estar en la misma carpeta que este .bat
    echo    Carpeta actual: %~dp0
    echo.
    pause
    exit /b 1
)

echo [CONFIG] Configurando permisos de PowerShell...
echo.

REM Configurar politica de ejecucion de PowerShell automaticamente
powershell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force" 2>nul

REM Verificar si PowerShell esta disponible
powershell -Command "Write-Host 'PowerShell OK'" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] PowerShell no esta disponible
    echo.
    echo    Necesitas Windows PowerShell para ejecutar este script
    echo.
    pause
    exit /b 1
)

echo [OK] PowerShell configurado correctamente
echo.
echo [INICIO] Iniciando respaldo...
echo.

REM Ejecutar el script de PowerShell con codificacion mejorada
powershell -ExecutionPolicy Bypass -Command "& '%~dp0backup_preformat.ps1'"

REM Verificar si el script se ejecuto correctamente
if %errorlevel% equ 0 (
    echo.
    echo [EXITO] RESPALDO COMPLETADO EXITOSAMENTE
    echo.
    echo [INFO] La carpeta de respaldo se abrio automaticamente
    echo [INFO] Copia esta carpeta a un USB o almacenamiento externo
    echo.
) else (
    echo.
    echo [ERROR] El script no se completo correctamente
    echo.
    echo [SOLUCION] Posibles soluciones:
    echo    - Ejecutar como administrador
    echo    - Verificar que los archivos esten en la misma carpeta
    echo    - Revisar los permisos del sistema
    echo.
)

echo.
echo Presiona cualquier tecla para salir...
pause >nul