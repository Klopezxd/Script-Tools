#Requires -Version 5.1
<#
.SYNOPSIS
    Instala accesos directos de Script-Tools en el menu contextual de Windows Explorer.
.DESCRIPTION
    Registra entradas en HKCU:\Software\Classes\SystemFileAssociations para videos (.mp4, .mkv, etc.)
    y documentos (.pdf). No requiere privilegios de Administrador.
#>

[CmdletBinding()]
param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Split-Path -Parent $PSScriptRoot)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Script-Tools - Instalador de Menu Contextual (Explorer)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "[INFO] Directorio base: $RepoRoot"

# Determinar el ejecutable o interprete a registrar
$ToolsExe = Join-Path $RepoRoot "tools.exe"
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$ToolsPy = Join-Path $RepoRoot "tools.py"

if (Test-Path $ToolsExe) {
    $CommandBase = "`"$ToolsExe`""
    $IconPath = "$ToolsExe,0"
    Write-Host "[OK] Detectado binario standalone: tools.exe" -ForegroundColor Green
} elseif (Test-Path $VenvPython) {
    $CommandBase = "`"$VenvPython`" `"$ToolsPy`""
    $IconPath = "imageres.dll,-102"
    Write-Host "[OK] Detectado entorno virtual: .venv" -ForegroundColor Green
} else {
    $CommandBase = "python `"$ToolsPy`""
    $IconPath = "imageres.dll,-102"
    Write-Host "[AVISO] tools.exe no encontrado; usando interprete global 'python'." -ForegroundColor Yellow
}

$VideoExts = @('.mp4', '.mkv', '.mov', '.avi', '.webm', '.flv', '.m4v', '.wmv', '.ts')
$PdfExts = @('.pdf')

# 1. Registrar para Video
Write-Host "`n[INFO] Registrando asociacion para archivos de video..."
foreach ($ext in $VideoExts) {
    $keyPath = "HKCU:\Software\Classes\SystemFileAssociations\$ext\shell\ScriptToolsVideo"
    $cmdKeyPath = "$keyPath\command"
    
    if (-not (Test-Path $keyPath)) {
        New-Item -Path $keyPath -Force | Out-Null
    }
    Set-ItemProperty -Path $keyPath -Name "(Default)" -Value "Comprimir con Script-Tools"
    Set-ItemProperty -Path $keyPath -Name "Icon" -Value $IconPath
    
    if (-not (Test-Path $cmdKeyPath)) {
        New-Item -Path $cmdKeyPath -Force | Out-Null
    }
    $cmdString = "cmd.exe /s /c `"$CommandBase video `"`%1`" & pause`""
    Set-ItemProperty -Path $cmdKeyPath -Name "(Default)" -Value $cmdString
}
Write-Host "[OK] $(${VideoExts}.Count) formatos de video asociados correctamente." -ForegroundColor Green

# 2. Registrar para PDF
Write-Host "[INFO] Registrando asociacion para documentos PDF..."
foreach ($ext in $PdfExts) {
    $keyPath = "HKCU:\Software\Classes\SystemFileAssociations\$ext\shell\ScriptToolsPDF"
    $cmdKeyPath = "$keyPath\command"
    
    if (-not (Test-Path $keyPath)) {
        New-Item -Path $keyPath -Force | Out-Null
    }
    Set-ItemProperty -Path $keyPath -Name "(Default)" -Value "Optimizar con Script-Tools"
    Set-ItemProperty -Path $keyPath -Name "Icon" -Value $IconPath
    
    if (-not (Test-Path $cmdKeyPath)) {
        New-Item -Path $cmdKeyPath -Force | Out-Null
    }
    $cmdString = "cmd.exe /s /c `"$CommandBase pdf `"`%1`" & pause`""
    Set-ItemProperty -Path $cmdKeyPath -Name "(Default)" -Value $cmdString
}
Write-Host "[OK] Archivos .pdf asociados correctamente." -ForegroundColor Green

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host " [EXITO] Menu contextual instalado con exito." -ForegroundColor Green
Write-Host " Ahora puedes hacer clic derecho sobre cualquier video o PDF" -ForegroundColor Green
Write-Host " y seleccionar 'Comprimir / Optimizar con Script-Tools'." -ForegroundColor Green
Write-Host " (En Windows 11, tambien disponible en 'Mostrar mas opciones')" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
