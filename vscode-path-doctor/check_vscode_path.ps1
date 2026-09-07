<#
.SYNOPSIS
    Diagnostica y repara la disponibilidad del comando CLI 'code' de Visual Studio Code en Windows.

.DESCRIPTION
    Verifica si 'code' esta disponible en el PATH del sistema, identifica si apunta a una instalacion
    legitima de VS Code (estable o Insiders) y ofrece reparacion temporal y permanente si la variable
    PATH se ha desconfigurado.
#>

[CmdletBinding()]
param(
    [switch]$AutoFix,
    [switch]$NonInteractive
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  [DOCTOR] VS CODE PATH DIAGNOSTIC & REPAIR" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Verificando disponibilidad del comando 'code' en PATH..." -ForegroundColor Gray

$possiblePaths = @(
    "$env:LOCALAPPDATA\Programs\Microsoft VS Code\bin",
    "$env:ProgramFiles\Microsoft VS Code\bin",
    "${env:ProgramFiles(x86)}\Microsoft VS Code\bin",
    "$env:LOCALAPPDATA\Programs\Microsoft VS Code Insiders\bin"
)

$validBinaries = @("Code.exe", "code.cmd", "Code - Insiders.exe", "code-insiders.cmd")

# 1. Comprobar si 'code' responde directamente
$commandFound = $false
$currentSource = $null

try {
    $codeCmd = Get-Command code -ErrorAction Stop
    $currentSource = $codeCmd.Source
    $commandFound = $true
} catch {
    $commandFound = $false
}

if ($commandFound) {
    Write-Host "   [OK] Comando encontrado en: $currentSource" -ForegroundColor Green

    $isLegit = $false
    foreach ($bin in $validBinaries) {
        if ($currentSource -like "*$bin*") {
            $isLegit = $true
            break
        }
    }

    if ($isLegit) {
        try {
            $versionOutput = & code --version 2>$null
            if ($versionOutput) {
                Write-Host "   [OK] Version detectada: $($versionOutput[0])" -ForegroundColor Green
                Write-Host "   [INFO] Arquitectura: $($versionOutput[2])" -ForegroundColor Gray
            }
        } catch {}
        Write-Host "   [OK] La integracion CLI de VS Code esta funcionando al 100%." -ForegroundColor Green
        Write-Host "========================================================" -ForegroundColor Cyan
        exit 0
    } else {
        Write-Host "   [AVISO] El comando 'code' encontrado no parece apuntar a VS Code oficial." -ForegroundColor Yellow
    }
} else {
    Write-Host "   [ERROR] El comando 'code' no esta disponible en la sesion actual." -ForegroundColor Red
}

# 2. Localizar instalacion fisica de VS Code
Write-Host ""
Write-Host "-> Buscando instalacion de Visual Studio Code en rutas estandar..." -ForegroundColor Cyan
$detectedDir = $null

foreach ($dir in $possiblePaths) {
    if (Test-Path -LiteralPath "$dir\code.cmd") {
        $detectedDir = $dir
        break
    }
}

if ($detectedDir) {
    Write-Host "   [OK] Instalacion detectada en: $detectedDir" -ForegroundColor Green
    Write-Host ""
    $shouldFix = $AutoFix
    if (-not $shouldFix -and -not $NonInteractive -and -not [Console]::IsInputRedirected) {
        $resp = Read-Host "Deseas agregar esta ruta al PATH de tu usuario de forma permanente? (s/n)"
        $shouldFix = ($resp.Trim().ToLower() -eq 's')
    }
    
    if ($shouldFix) {
        try {
            $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
            if ($userPath -notlike "*$detectedDir*") {
                $newPath = "$userPath;$detectedDir"
                [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
                $env:PATH = "$detectedDir;" + $env:PATH
                Write-Host "   [OK] Ruta agregada al PATH de usuario permanentemente." -ForegroundColor Green
                Write-Host "   [INFO] Las nuevas terminales que abras ya tendran el comando 'code' listo." -ForegroundColor Yellow
            } else {
                Write-Host "   [INFO] La ruta ya estaba presente en el PATH de usuario." -ForegroundColor Gray
            }
        } catch {
            Write-Host "   [ERROR] Error al actualizar el PATH: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        # Agregar solo a sesion actual
        $env:PATH = "$detectedDir;" + $env:PATH
        Write-Host "   [INFO] Ruta anadida temporalmente solo a la sesion actual." -ForegroundColor Yellow
    }
} else {
    Write-Host "   [ERROR] No se encontro ninguna instalacion de VS Code en las rutas habituales." -ForegroundColor Red
    Write-Host "   [RECOMENDACION] En VS Code, presiona Ctrl+Shift+P y escribe Shell Command: Install code command in PATH." -ForegroundColor Yellow
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
