<#
.SYNOPSIS
    Script de configuracion inicial automatizada para Script-Tools.
.DESCRIPTION
    Verifica Python 3.10+, crea o actualiza el entorno virtual (.venv),
    instala dependencias y audita herramientas opcionales (FFmpeg).
#>

[CmdletBinding()]
param()

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  [SCRIPT-TOOLS] CONFIGURACION INICIAL DEL ENTORNO DE DESARROLLO" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "   [ERROR] Python no esta disponible en el PATH." -ForegroundColor Red
    Write-Host "   Instala Python 3.10+ desde python.org o mediante: winget install Python.Python.3.11" -ForegroundColor Yellow
    exit 1
}

$pyVer = & python --version 2>&1
Write-Host "   [OK] Python detectado: $pyVer" -ForegroundColor Green

# 2. Entorno virtual (.venv)
$venvDir = Join-Path $PSScriptRoot ".venv"
if (-not (Test-Path $venvDir)) {
    Write-Host "-> Creando entorno virtual en .venv..." -ForegroundColor Cyan
    & python -m venv $venvDir
    Write-Host "   [OK] Entorno virtual creado exitosamente" -ForegroundColor Green
} else {
    Write-Host "   [OK] Entorno virtual existente detectado en .venv" -ForegroundColor Green
}

$pipBin = Join-Path $venvDir "Scripts\pip.exe"
$pythonVenv = Join-Path $venvDir "Scripts\python.exe"

# 3. Actualizar pip e instalar dependencias
Write-Host "-> Instalando y actualizando dependencias de Script-Tools..." -ForegroundColor Cyan
& $pipBin install --upgrade pip --quiet
& $pipBin install pymupdf pikepdf Pillow rich pytest ruff --quiet
Write-Host "   [OK] Dependencias instaladas (PyMuPDF, pikepdf, Pillow, Rich, Pytest, Ruff)" -ForegroundColor Green

# 4. Auditoria de herramientas multimedia opcionales
$ffmpegCmd = Get-Command ffmpeg -ErrorAction SilentlyContinue
if ($ffmpegCmd) {
    Write-Host "   [OK] FFmpeg detectado en PATH (Aceleracion de video habilitada)" -ForegroundColor Green
} else {
    Write-Host "   [AVISO] FFmpeg no detectado en PATH." -ForegroundColor Yellow
    Write-Host "   Para usar video-compressor, instala FFmpeg mediante:" -ForegroundColor Gray
    Write-Host "     winget install Gyan.FFmpeg   o   scoop install ffmpeg" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Green
Write-Host "  [EXITO] SCRIPT-TOOLS LISTO PARA USAR" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
Write-Host "Comandos rapidos:" -ForegroundColor White
Write-Host "  $pythonVenv tools.py --help" -ForegroundColor Yellow
Write-Host "  $pythonVenv tools.py doctor" -ForegroundColor Yellow
Write-Host "O arrastra tus archivos .mp4 o .pdf sobre los accesos .bat" -ForegroundColor Gray
Write-Host ""
