#Requires -Version 5.1
<#
.SYNOPSIS
    Desinstala los accesos directos de Script-Tools del menu contextual de Windows Explorer.
.DESCRIPTION
    Elimina las claves registradas en HKCU:\Software\Classes\SystemFileAssociations.
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "SilentlyContinue"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Script-Tools - Desinstalador de Menu Contextual (Explorer)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$VideoExts = @('.mp4', '.mkv', '.mov', '.avi', '.webm', '.flv', '.m4v', '.wmv', '.ts')
$PdfExts = @('.pdf')

$removedCount = 0

foreach ($ext in $VideoExts) {
    $keyPath = "HKCU:\Software\Classes\SystemFileAssociations\$ext\shell\ScriptToolsVideo"
    if (Test-Path $keyPath) {
        Remove-Item -Path $keyPath -Recurse -Force -ErrorAction SilentlyContinue
        $removedCount++
    }
}

foreach ($ext in $PdfExts) {
    $keyPath = "HKCU:\Software\Classes\SystemFileAssociations\$ext\shell\ScriptToolsPDF"
    if (Test-Path $keyPath) {
        Remove-Item -Path $keyPath -Recurse -Force -ErrorAction SilentlyContinue
        $removedCount++
    }
}

Write-Host "[OK] Entradas del menu contextual eliminadas ($removedCount elementos limpiados)." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
