<#
.SYNOPSIS
    Comprime archivos de video utilizando FFmpeg y el códec H.265 (HEVC).

.DESCRIPTION
    Reduce drásticamente el peso de videos manteniendo una calidad visual óptima.
    Soporta ejecución por terminal, arrastrar y soltar (drag & drop) y selector gráfico si se omite el archivo.

.PARAMETER InputFile
    Ruta al video a comprimir. Si se omite, se abrirá un cuadro de diálogo para seleccionarlo.

.PARAMETER Resolution
    Resolución vertical objetivo (por defecto: 480). Opciones comunes: 480, 720, 1080.

.PARAMETER CRF
    Factor de tasa constante (Constant Rate Factor). Por defecto 35 (mayor número = mayor compresión).

.PARAMETER Preset
    Preset de velocidad de codificación de x265 (ultrafast, fast, medium, slow). Por defecto: slow.

.PARAMETER AudioBitrate
    Tasa de bits de audio AAC (por defecto: 64k).

.EXAMPLE
    .\compress_video.ps1 -InputFile "clase.mp4"
    .\compress_video.ps1 -InputFile "grabacion.mkv" -Resolution 720 -CRF 28
#>

[CmdletBinding()]
param (
    [Parameter(Mandatory=$false, Position=0)]
    [string]$InputFile,

    [ValidateSet("360", "480", "720", "1080")]
    [string]$Resolution = "480",

    [ValidateRange(18, 45)]
    [int]$CRF = 35,

    [ValidateSet("ultrafast", "fast", "medium", "slow", "slower")]
    [string]$Preset = "slow",

    [string]$AudioBitrate = "64k"
)

# 1. Configurar codificación de consola
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 2. Verificar disponibilidad de FFmpeg
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] FFmpeg no está disponible en el PATH del sistema." -ForegroundColor Red
    Write-Host "Descárgalo de https://ffmpeg.org y agrégalo a las variables de entorno." -ForegroundColor Yellow
    exit 1
}

# 3. Obtener archivo de entrada (terminal o diálogo gráfico)
if ([string]::IsNullOrWhiteSpace($InputFile)) {
    Add-Type -AssemblyName System.Windows.Forms
    $dialog = New-Object System.Windows.Forms.OpenFileDialog
    $dialog.Title = "Selecciona el video a comprimir"
    $dialog.Filter = "Videos (*.mp4;*.avi;*.mov;*.mkv;*.wmv;*.flv;*.webm)|*.mp4;*.avi;*.mov;*.mkv;*.wmv;*.flv;*.webm|Todos los archivos (*.*)|*.*"
    
    if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
        $InputFile = $dialog.FileName
    } else {
        Write-Host "Operación cancelada por el usuario." -ForegroundColor Yellow
        exit 0
    }
}

if (-not (Test-Path -LiteralPath $InputFile)) {
    Write-Host "[ERROR] El archivo especificado no existe: $InputFile" -ForegroundColor Red
    exit 1
}

$validExtensions = @('.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.m4v', '.webm')
$extension = [System.IO.Path]::GetExtension($InputFile).ToLower()
if ($extension -notin $validExtensions) {
    Write-Host "[ERROR] Formato no soportado: $extension" -ForegroundColor Red
    exit 1
}

$inputItem = Get-Item -LiteralPath $InputFile
$outputFile = Join-Path $inputItem.Directory.FullName "$($inputItem.BaseName)_comp.mp4"

$originalSizeMB = [math]::Round($inputItem.Length / 1MB, 2)

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " 🎬 COMPRESOR DE VIDEO X265 (HEVC)" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " ▶️ Video Origen:  $($inputItem.Name) ($originalSizeMB MB)" -ForegroundColor White
Write-Host " ⚙️ Configuración: {$Resolution}p | CRF: $CRF | Preset: $Preset | Audio: $AudioBitrate" -ForegroundColor Gray
Write-Host " ➡️ Video Salida:  $([System.IO.Path]::GetFileName($outputFile))" -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$ffmpegArgs = @(
    "-i", "`"$InputFile`"",
    "-vf", "`"scale=-2:$Resolution`"",
    "-c:v", "libx265",
    "-crf", "$CRF",
    "-preset", "$Preset",
    "-c:a", "aac",
    "-b:a", "$AudioBitrate",
    "-y",
    "`"$outputFile`""
)

$commandString = "ffmpeg " + ($ffmpegArgs -join " ")
Invoke-Expression $commandString

if (Test-Path -LiteralPath $outputFile) {
    $finalItem = Get-Item -LiteralPath $outputFile
    $finalSizeMB = [math]::Round($finalItem.Length / 1MB, 2)
    $savedPct = [math]::Round((($inputItem.Length - $finalItem.Length) / $inputItem.Length) * 100, 1)

    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Green
    Write-Host " ✅ Compresión completada exitosamente!" -ForegroundColor Green
    Write-Host " 📊 Peso original: $originalSizeMB MB" -ForegroundColor Gray
    Write-Host " 📉 Peso final:    $finalSizeMB MB" -ForegroundColor Green
    Write-Host " 💾 Ahorro:        $savedPct%" -ForegroundColor Yellow
    Write-Host " 📁 Guardado en:   $outputFile" -ForegroundColor White
    Write-Host "========================================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[ERROR] No se pudo generar el archivo comprimido." -ForegroundColor Red
    exit 1
}
