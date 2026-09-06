# 🎥 Video Compressor H.265 (HEVC)

Script de compresión de video de alta eficiencia con **FFmpeg** utilizando el códec x265 para reducir el tamaño de videos hasta un 80% manteniendo legibilidad y nitidez.

## 🌟 Características
* **Códec x265 (HEVC):** Máxima relación compresión/calidad.
* **Resolución adaptable:** Escala inteligente a 480p, 720p o 1080p manteniendo el aspect ratio.
* **Triple modo de ejecución:**
  * Arrastrar y soltar (*Drag & Drop*) sobre `compress_video.bat`.
  * Selección gráfica de archivo automática si se ejecuta sin parámetros.
  * Línea de comandos con flags personalizables en PowerShell.

## 📋 Requisitos
* Windows 10/11 o PowerShell 5.1+
* **FFmpeg** instalado y agregado al PATH del sistema (`ffmpeg -version`).

## 💻 Uso

### 1. Arrastrar y Soltar
Arrastra cualquier video (`.mp4`, `.mkv`, `.avi`, `.mov`, etc.) directamente sobre `compress_video.bat`.

### 2. Desde PowerShell
```powershell
# Compresión estándar (480p, CRF 35):
.\compress_video.ps1 -InputFile "clase.mp4"

# Calidad superior (720p, CRF 28, preset medium):
.\compress_video.ps1 -InputFile "conferencia.mkv" -Resolution 720 -CRF 28 -Preset medium
```
