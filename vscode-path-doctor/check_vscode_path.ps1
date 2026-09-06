<#
.SYNOPSIS
    Diagnostica y repara la disponibilidad del comando CLI 'code' de Visual Studio Code en Windows.

.DESCRIPTION
    Verifica si 'code' está disponible en el PATH del sistema, identifica si apunta a una instalación
    legítima de VS Code (estable o Insiders) y ofrece reparación temporal y permanente si la variable
    PATH se ha desconfigurado.
#>

[CmdletBinding()]
param()

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " 🩺 VS CODE PATH DOCTOR" -ForegroundColor Cyan
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
    Write-Host "✅ Comando encontrado en: $currentSource" -ForegroundColor Green

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
                Write-Host "📦 Versión detectada: $($versionOutput[0])" -ForegroundColor Green
                Write-Host "Arquitectura: $($versionOutput[2])" -ForegroundColor Gray
            }
        } catch {}
        Write-Host "🎉 La integración CLI de VS Code está funcionando al 100%." -ForegroundColor Green
        Write-Host "========================================================" -ForegroundColor Cyan
        exit 0
    } else {
        Write-Host "⚠️ AVISO: El comando 'code' encontrado no parece apuntar a VS Code oficial." -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ ERROR: El comando 'code' no está disponible en la sesión actual." -ForegroundColor Red
}

# 2. Localizar instalación física de VS Code
Write-Host "`n🔍 Buscando instalación de Visual Studio Code en rutas estándar..." -ForegroundColor Cyan
$detectedDir = $null

foreach ($dir in $possiblePaths) {
    if (Test-Path -LiteralPath "$dir\code.cmd") {
        $detectedDir = $dir
        break
    }
}

if ($detectedDir) {
    Write-Host "✅ Instalación detectada en: $detectedDir" -ForegroundColor Green
    Write-Host ""
    $resp = Read-Host "¿Deseas agregar esta ruta al PATH de tu usuario de forma permanente? (s/n)"
    
    if ($resp.Trim().ToLower() -eq 's') {
        try {
            $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
            if ($userPath -notlike "*$detectedDir*") {
                $newPath = "$userPath;$detectedDir"
                [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
                $env:PATH = "$detectedDir;" + $env:PATH
                Write-Host "🎉 ¡Éxito! Ruta agregada al PATH de usuario permanentemente." -ForegroundColor Green
                Write-Host "Nota: Las nuevas terminales que abras ya tendrán el comando 'code' listo." -ForegroundColor Yellow
            } else {
                Write-Host "ℹ️ La ruta ya estaba presente en el PATH de usuario." -ForegroundColor Gray
            }
        } catch {
            Write-Host "❌ Error al actualizar el PATH: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        # Agregar solo a sesión actual
        $env:PATH = "$detectedDir;" + $env:PATH
        Write-Host "⚡ Ruta añadida temporalmente solo a la sesión actual." -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ No se encontró ninguna instalación de VS Code en las rutas habituales." -ForegroundColor Red
    Write-Host "💡 Recomendación: Abre VS Code, presiona Ctrl+Shift+P y escribe: 'Shell Command: Install code command in PATH'." -ForegroundColor Yellow
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
