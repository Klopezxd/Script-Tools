# ==============================================================================
# Script de Reinstalacion Post-Formateo - Entorno de Desarrollo Windows
# ==============================================================================
[CmdletBinding()]
param(
    [switch]$NoPause
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Green
Write-Host "  [SCRIPT-TOOLS] RESTAURACION POST-FORMATEO DE ENTORNO DEV" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
Write-Host ""

# 1. Winget
if (Test-Path "REINSTALL_winget_packages.json") {
    $ans = Read-Host "Deseas reinstalar los paquetes de Winget? (s/n)"
    if ($ans.ToLower() -eq "s") {
        Write-Host "Restaurando aplicaciones con Winget..." -ForegroundColor Yellow
        winget import -i "REINSTALL_winget_packages.json" --accept-source-agreements --accept-package-agreements
    }
}

# 2. Scoop
if (Test-Path "REINSTALL_scoop_apps.txt") {
    $ans = Read-Host "Deseas reinstalar las herramientas de Scoop? (s/n)"
    if ($ans.ToLower() -eq "s") {
        if (-not (Get-Command scoop -ErrorAction SilentlyContinue)) {
            Write-Host "Instalando Scoop..." -ForegroundColor Yellow
            Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
            irm get.scoop.co | iex
        }
        Write-Host "Restaurando apps de Scoop..." -ForegroundColor Yellow
        Get-Content "REINSTALL_scoop_apps.txt" | ForEach-Object {
            $app = $_.Trim()
            if ($app) { scoop install $app }
        }
    }
}

# 3. Extensiones de VS Code
if (Test-Path "REINSTALL_vscode_extensions.txt") {
    $ans = Read-Host "Deseas reinstalar las extensiones de Visual Studio Code? (s/n)"
    if ($ans.ToLower() -eq "s") {
        if (Get-Command code -ErrorAction SilentlyContinue) {
            Get-Content "REINSTALL_vscode_extensions.txt" | ForEach-Object {
                $ext = $_.Trim()
                if ($ext) {
                    Write-Host "Instalando extension: $ext" -ForegroundColor Cyan
                    code --install-extension $ext --force
                }
            }
        } else {
            Write-Host "[AVISO] Instala VS Code primero para restaurar sus extensiones." -ForegroundColor Yellow
        }
    }
}

# 4. Pip packages
if (Test-Path "REINSTALL_requirements.txt") {
    $ans = Read-Host "Deseas reinstalar los paquetes de Python (pip)? (s/n)"
    if ($ans.ToLower() -eq "s") {
        pip install -r "REINSTALL_requirements.txt"
    }
}

# 5. Git Config
if (Test-Path "REINSTALL_git_config.txt") {
    Write-Host "Aplicando configuracion global de Git..." -ForegroundColor Yellow
    Get-Content "REINSTALL_git_config.txt" | ForEach-Object {
        $line = $_.Trim()
        $idx = $line.IndexOf('=')
        if ($idx -gt 0) {
            $key = $line.Substring(0, $idx).Trim()
            $val = $line.Substring($idx + 1).Trim()
            git config --global "$key" "$val"
        }
    }
    Write-Host "[OK] Git configurado" -ForegroundColor Green
}

# 6. Configuracion de VS Code (settings.json)
if (Test-Path "VSCode_Config\settings.json") {
    $targetDir = "$env:APPDATA\Code\User"
    if (Test-Path $targetDir) {
        Copy-Item "VSCode_Config\settings.json" -Destination "$targetDir\settings.json" -Force
        Write-Host "[OK] settings.json de VS Code restaurado" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "   [OK] Proceso de restauracion concluido." -ForegroundColor Green
Write-Host ""
if (-not $NoPause) {
    pause
}
