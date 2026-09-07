# Video Compressor

Herramienta de compresión de video multiplataforma de alto rendimiento basada en **FFmpeg**. Diseñada para maximizar el ahorro de espacio mediante detección automática de aceleración por hardware (GPU), cálculo de tasa de bits a dos pasadas para límites de plataformas de mensajería (WhatsApp, Discord) y perfiles CRF de alta fidelidad.

---

## Características

* **Detección Automática de GPU:** Detecta y aprovecha automáticamente encoders de hardware:
  * **NVIDIA:** `hevc_nvenc`, `h264_nvenc`, `av1_nvenc`
  * **Apple Silicon / macOS:** `hevc_videotoolbox`, `h264_videotoolbox`
  * **Intel:** `hevc_qsv`, `h264_qsv`, `av1_qsv`
  * **AMD:** `hevc_amf`, `h264_amf`
  * **CPU Fallback:** `libx265`, `libx264`, `libsvtav1`, `libvpx-vp9`
* **Modo Target Size (2 Pasadas):** Calcula matemáticamente la tasa de bits exacta en función de la duración para cumplir límites estrictos (por ejemplo, exactamente 10 MB para Discord Free o 16 MB para WhatsApp):
  $$\text{Bitrate}_{\text{video}} = \frac{\text{Bytes}_{\text{objetivo}} \times 8}{\text{Duración (s)}} - \text{Bitrate}_{\text{audio}}$$
* **Soporte Multi-Códec:**
  * **AV1:** Compresión de última generación con la mayor eficiencia posible.
  * **HEVC (H.265):** Excelente equilibrio compresión/calidad para dispositivos modernos.
  * **H.264 (AVC):** Compatibilidad universal absoluta (navegadores antiguos, Smart TVs).
  * **VP9:** Optimizado para la web y plataformas abiertas.
* **Escalado Seguro:** `original`, `1080p`, `720p`, `480p`, garantizando dimensiones pares requeridas por codificadores `yuv420p`.
* **Procesamiento por Lotes (Batch):** Comprime carpetas enteras de videos de forma desatendida.
* **Interfaz Versátil:** Línea de comandos (CLI), selector gráfico nativo interactivo y *Drag & Drop* en Windows (`compress_video.bat`).

---

## Requisitos

1. **Python 3.10+**
2. **FFmpeg y FFprobe** instalados y registrados en el PATH del sistema:
   * **Windows:** `scoop install ffmpeg` o `winget install Gyan.FFmpeg`
   * **macOS:** `brew install ffmpeg`
   * **Linux:** `sudo apt install ffmpeg`

---

## Guía de Uso

### 1. Menú Contextual de Windows (Clic Derecho)
Instala los accesos directos ejecutando `scripts/install_context_menu.bat` en la raíz.
Luego haz **clic derecho** sobre cualquier archivo de video (`.mp4`, `.mkv`, `.mov`, etc.) y selecciona:
> **Comprimir con Script-Tools**

### 2. Arrastrar y Soltar (Drag & Drop)
Arrastra cualquier video sobre `compress_video.bat` en el Explorador de Windows. Se ejecutará inmediatamente en modo equilibrado con barra de progreso en vivo.

### 3. Línea de Comandos (CLI)
```bash
# Vía CLI Unificada (raíz)
python tools.py video clase.mp4 --target-size 15MB

# O directamente desde este directorio
python compress_video.py clase.mp4 --target-size 15MB
```

---

## Recetas Frecuentes

| Objetivo | Comando | Explicación Técnica |
|---|---|---|
| **WhatsApp (< 16 MB)** | `python tools.py video video.mp4 -t 15MB` | 2 pasadas exactas para garantizar envío sin compresión destructiva de WhatsApp. |
| **Discord Free (< 25 MB)** | `python tools.py video gameplay.mkv -t 25MB -c h264` | H.264 para reproducción nativa inline en cliente web y desktop de Discord. |
| **Calidad de Archivo (AV1)** | `python tools.py video cine.mp4 -c av1 -p high` | SVT-AV1 de última generación, máxima reducción manteniendo fidelidad visual. |
| **Rápido por GPU (NVIDIA)** | `python tools.py video render.mp4 --hwaccel nvenc -p draft` | NVENC por hardware a máxima velocidad (~10x más rápido que CPU). |
| **Reducir 4K a 1080p** | `python tools.py video camara.mov -r 1080p -p balanced` | Re-escalado simétrico par (`scale=-2:1080`) para compatibilidad YUV420p. |
| **Lote de Videos (Batch)** | `python tools.py video ./grabaciones --batch -r 720p` | Procesa desatendidamente todos los videos de la carpeta. |

---

## Parámetros de CLI

| Argumento | Opciones | Por Defecto | Descripción |
|---|---|---|---|
| `input` | Ruta a archivo o carpeta | *GUI Picker* | Video o directorio a procesar. Si se omite, abre diálogo nativo. |
| `-o, --output` | Ruta de archivo | `[nombre]_compressed.mp4` | Ruta de salida personalizada. |
| `-c, --codec` | `hevc`, `h264`, `av1`, `vp9` | `hevc` | Códec de video destino. |
| `-p, --preset` | `archival`, `high`, `balanced`, `draft` | `balanced` | Perfil de calidad CRF. |
| `-r, --resolution`| `keep`, `1080p`, `720p`, `480p`, `360p` | `keep` | Resolución vertical máxima. |
| `-t, --target-size`| e.g. `10MB`, `25MB`, `700KB` | *Ninguno* | Activa compresión matemática de 2 pasadas a peso exacto. |
| `--hwaccel` | `auto`, `cpu`, `nvenc`, `videotoolbox`, `qsv`, `amf` | `auto` | Preferencia de codificador por hardware. |
| `--crf` | Entero (e.g. 24) | *Auto por preset* | Sobrescribe manualmente el valor CRF. |
| `--audio` | `aac`, `copy`, `opus`, `mute` | `aac` | Tratamiento de pistas de audio. |
| `--audio-bitrate` | e.g. `64k`, `128k` | `64k` | Tasa de bits de la pista de audio. |
| `--speed` | `ultrafast` a `veryslow` | `medium` | Preset de velocidad de CPU. |
| `--batch` | Flag booleano | `False` | Procesa todos los videos en la carpeta especificada. |

