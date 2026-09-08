# Script-Tools

[![CI](https://img.shields.io/github/actions/workflow/status/Klopezxd/Script-Tools/ci.yml?branch=main&label=CI&logo=githubactions&logoColor=white&style=flat-square)](https://github.com/Klopezxd/Script-Tools/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/Klopezxd/Script-Tools?style=flat-square&logo=github&logoColor=white&label=Release)](https://github.com/Klopezxd/Script-Tools/releases)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

Colección modular de herramientas de automatización para desarrolladores y usuarios finales: compresión multimedia acelerada por GPU, optimización extrema de documentos PDF con preservación estricta de OCR y firmas digitales, diagnóstico integral de entornos de desarrollo y respaldos pre-formateo.

Diseñado para usarse **como tú prefieras**: mediante un menú visual interactivo en 1 clic, integración al menú contextual del Explorador de Windows, arrastrar y soltar (Drag & Drop) o línea de comandos profesional (CLI / binarios autónomos).

---

## 🚀 ¿Cómo usar Script-Tools? (Elige tu método favorito)

No necesitas ser un experto en terminal para usar las herramientas. Dispones de cuatro formas de ejecución según tu preferencia:

### 1. 🖱️ Menú Visual e Interactivo (El más fácil — ¡Sin escribir comandos!)
* **En Windows:** Haz doble clic directamente sobre [**`tools.bat`**](tools.bat).
* **En Linux & macOS:** Ejecuta en terminal [**`./tools.sh`**](tools.sh) (o `bash tools.sh`).
* **Desde cualquier consola:** Ejecuta `python tools.py menu`.

> **¿Qué hace?** Abre una interfaz visual en la consola con selección por números o flechas. Te permite elegir la herramienta, abre una ventana nativa de tu explorador para que selecciones tus archivos con el mouse, te guía en los ajustes de calidad y **mantiene la ventana abierta al finalizar** para que veas los resultados de compresión con calma.

---

### 2. 📂 Clic Derecho en el Explorador de Windows (Menú Contextual)
Integra las herramientas directamente en el botón secundario del mouse en Windows (instalación limpia a nivel de usuario en `HKCU`, sin requerir permisos de Administrador):

1. Haz doble clic en [`scripts/install_context_menu.bat`](scripts/install_context_menu.bat).
2. ¡Listo! Ahora solo haz **clic derecho** sobre cualquier archivo:
   * **Videos (`.mp4`, `.mkv`, `.mov`, `.avi`, `.webm`):** Clic derecho > *"Comprimir con Script-Tools"*.
   * **Documentos (`.pdf`):** Clic derecho > *"Optimizar con Script-Tools"*.
3. Si deseas desinstalarlo en el futuro, haz doble clic en [`scripts/uninstall_context_menu.bat`](scripts/uninstall_context_menu.bat).

---

### 3. 📦 Arrastrar y Soltar (Drag & Drop)
Cada herramienta en [`tools/`](tools/) funciona de forma completamente independiente:
* **Comprimir Video:** Arrastra tu archivo de video directamente sobre [`tools/video-compressor/compress_video.bat`](tools/video-compressor/compress_video.bat).
* **Optimizar PDF:** Arrastra tu PDF sobre [`tools/pdf-optimizer/pdf_optimizer.bat`](tools/pdf-optimizer/pdf_optimizer.bat).
* **Reparar PATH de VS Code:** Doble clic a [`tools/vscode-path-doctor/check_vscode_path.bat`](tools/vscode-path-doctor/check_vscode_path.bat).

---

### 4. 💻 Línea de Comandos Profesional (CLI Central / Automatización)
Para desarrolladores, scripts desatendidos o pipelines de automatización, usa `tools.py` en la raíz:

```bash
# Menú interactivo visual
python tools.py menu

# Comprimir video a tamaño estricto para WhatsApp (< 16 MB) o Discord (< 25 MB)
python tools.py video clase.mp4 --target-size 15MB

# Comprimir video con GPU (NVIDIA, Intel, AMD, Apple) en códec AV1 o HEVC
python tools.py video gameplay.mkv --codec av1 --preset high --resolution 1080p

# Optimizar PDF con perfil extremo (reduce hasta un 94% sin tocar texto ni firmas)
python tools.py pdf documento.pdf --profile extreme

# Auditar salud de compiladores, Git, VS Code y runtimes
python tools.py doctor

# Crear snapshot de paquetes y configuración antes de formatear tu PC
python tools.py backup
```

---

## 🛠️ Herramientas Incluidas (`tools/`)

| Herramienta | Directorio | Plataforma | Capacidades Principales | Ejecución Rápida |
|---|---|---|---|---|
| **PDF Optimizer** | [`tools/pdf-optimizer/`](tools/pdf-optimizer/) | Multiplataforma | Compresión de hasta **-94%**. **Preservación estricta de OCR, texto vectorial, sellos y firmas digitales transparentes (`/SMask`)**. | `python tools.py pdf <file> --profile extreme` |
| **Video Compressor** | [`tools/video-compressor/`](tools/video-compressor/) | Multiplataforma | Compresión multi-códec (**AV1, HEVC/H.265, H.264, VP9**), aceleración por GPU (NVENC, VideoToolbox, QSV, AMF) y modo **Target Size a 2 pasadas**. | `python tools.py video <file> --target-size 15MB` |
| **Dev Environment Doctor** | [`tools/vscode-path-doctor/`](tools/vscode-path-doctor/) | Multiplataforma | Auditoría de compiladores (C++, CMake, Ninja, Git, runtimes) y **reparación en 1 clic del comando `code` en Windows**. | `python tools.py doctor` |
| **Developer Backup Pre-Format** | [`tools/system-backup-preformat/`](tools/system-backup-preformat/) | Multiplataforma | Respaldo total previo a formateo (Winget, Scoop, VS Code, Brew, APT, Pacman). Genera script de auto-restauración (`REINSTALL.ps1`). | `python tools.py backup` |

---

## 📄 Detalle: PDF Optimizer (OCR-Safe & Blindaje de Firmas)

Diseñado específicamente para resolver el problema común de los compresores de PDF online que destruyen documentos oficiales:

1. **Blindaje de Firmas Digitales y Transparencias (`/SMask`):** Sincroniza matemáticamente la imagen base y el canal alfa vectorial de las firmas y sellos. **Elimina para siempre los recuadros negros** y la pérdida de transparencia.
2. **Protección de Membretes y Marcas de Agua (`/Mask`):** Las marcas de agua transparentes nunca se aplanan sobre blanco opaco, garantizando que el texto, notas y tablas permanezcan **100% visibles y legibles**.
3. **Escalado Adaptativo por Bounding Box:** Calcula los DPI reales según el espacio físico que ocupa cada elemento en la hoja. Los códigos QR y firmas se reducen con nitidez quirúrgica sin pixelarse.
4. **Preservación de Capa OCR y Texto Vectorial:** El texto sigue siendo seleccionable, copiable y apto para búsquedas (`Ctrl+F`), siendo válido para universidades, trámites públicos o reclutadores internacionales.

### Perfiles de Compresión PDF:

| Perfil | DPI | Calidad JPEG | Reducción Típica | Caso de Uso Recomendado |
|---|---|---|---|---|
| `extreme` | 72 DPI | 45 | **75% - 95%** | Cuotas estrictas (< 2 MB), portales universitarios y WhatsApp (preserva 100% texto y firmas). |
| `screen` | 72 DPI | 50 | **70% - 90%** | Aulas virtuales (Moodle, Teams) con cuotas moderadas (< 5 MB). |
| `balanced` | 150 DPI | 75 | **50% - 80%** | Reportes académicos, diapositivas y envío por email [Recomendado general]. |
| `print` | 300 DPI | 85 | **30% - 60%** | Documentos formales para impresión física o portafolios. |
| `lossless` | Original | Sin re-muestreo | **10% - 35%** | Tesis y contratos legales vectoriales (0% alteración visual). |

---

## 🎬 Detalle: Video Compressor (GPU & Target Size)

* **Detección Automática de Hardware:** Aprovecha automáticamente tarjetas gráficas dedicadas para comprimir hasta **10x más rápido** que por CPU:
  * **NVIDIA:** `hevc_nvenc`, `h264_nvenc`, `av1_nvenc`
  * **Intel:** `hevc_qsv`, `h264_qsv`, `av1_qsv`
  * **AMD:** `hevc_amf`, `h264_amf`
  * **Apple Silicon:** `hevc_videotoolbox`, `h264_videotoolbox`
* **Modo Target Size Matemático (2 Pasadas):**
  Calcula la tasa de bits exacta en función de la duración del video:
  $$\text{Bitrate}_{\text{video}} = \frac{\text{Bytes}_{\text{objetivo}} \times 8}{\text{Duración (s)}} - \text{Bitrate}_{\text{audio}}$$
  * `--target-size 15MB`: Entra perfecto en el límite de WhatsApp sin que la app aplique compresión destructiva.
  * `--target-size 25MB`: Límite exacto de cuentas gratuitas de Discord.
* **Auto-Detección de FFmpeg:** Si FFmpeg fue instalado mediante Winget, Scoop o Chocolatey pero no se ha reiniciado la terminal, el script lo localiza y lo ejecuta automáticamente sin arrojar errores.

---

## 🩺 Detalle: Dev Doctor & Reparador de VS Code

* **Dev Doctor:** Audita el estado de salud de tu entorno de desarrollo en una tabla coloreada:
  * Compiladores C/C++: Clang, GCC, MSVC (`cl.exe`).
  * Build Systems: CMake, Ninja.
  * Control de versiones: Git, identidad de usuario (`user.name`, `user.email`).
  * Runtimes: Python, Node.js, .NET SDK, Rust.
* **Reparador de PATH de VS Code (Windows):** Si al escribir `code .` en tu consola recibes `'code' no se reconoce como un comando`, este módulo localiza la instalación en `%LOCALAPPDATA%` y repara el Registro de Windows de inmediato sin reiniciar la PC.

---

## 📦 Detalle: Developer Backup Pre-Format

¿Vas a formatear tu equipo o migrar a una nueva computadora?
1. Ejecuta `python tools.py backup` (o haz doble clic en `tools/system-backup-preformat/backup_preformat.bat`).
2. La herramienta exporta listas completas de tus paquetes instalados en **Winget, Scoop, extensiones y configuraciones de VS Code, claves de registro y variables de entorno**.
3. **Genera un script `REINSTALL.ps1` listo:** En tu nueva instalación de Windows, solo ejecutas ese script y volverá a instalar todos tus programas y extensiones automáticamente.

---

## ⚙️ Instalación y Configuración

### Opción A: Configuración Automatizada en 1 Clic (Recomendada)
* **En Windows:** Haz doble clic en [**`setup.bat`**](setup.bat) (o ejecuta `.\setup.ps1` en PowerShell).
* **En Linux & macOS:** Ejecuta:
  ```bash
  chmod +x setup.sh tools.sh
  ./setup.sh
  ```
El asistente crea el entorno virtual (`.venv`), actualiza `pip`, instala las dependencias y valida la presencia de `ffmpeg`.

### Opción B: Ejecutable Autónomo Standalone (Sin Requerir Python)
Si no deseas instalar Python ni configurar entornos virtuales, descarga el binario precompilado independiente desde [**Releases**](https://github.com/Klopezxd/Script-Tools/releases):
* **Windows:** `tools-windows-x64.exe` (puedes colocarlo en tu PATH o renombrarlo a `tools.exe`).
* **Linux:** `tools-linux-x64`.
* **macOS:** `tools-macos-universal`.

### Opción C: Instalación Manual
```bash
git clone https://github.com/Klopezxd/Script-Tools.git
cd Script-Tools
pip install -r tools/pdf-optimizer/requirements.txt
```

---

## ⌨️ Autocompletado de Terminal

Habilita autocompletado nativo para todos los subcomandos y parámetros técnicos (`--codec`, `--preset`, `--target-size`, `--hwaccel`, etc.):

```powershell
# En PowerShell (agregar a tu $PROFILE para persistencia):
tools completion powershell | Out-String | Invoke-Expression

# En Bash:
eval "$(tools completion bash)"

# En Zsh:
source <(tools completion zsh)
```

---

## 🧪 Suite de Pruebas y Calidad de Código

El repositorio cuenta con una suite rigurosa de pruebas automatizadas unitarias y de integración en **Pytest**:

```bash
# Ejecutar suite de pruebas completa (44 pruebas)
pytest -v

# Verificar análisis estático y formato con Ruff
ruff check .
ruff format --check .
```

---

## 📁 Estructura del Repositorio

```text
Script-Tools/
├── .github/                      # Automatización CI/CD (Ubuntu, Windows, macOS)
├── scripts/                      # Utilidades de instalación (menú contextual Explorer)
├── tests/                        # Suite automatizada de pruebas QA (Pytest - 44 pruebas)
├── tools/                        # 👈 TODAS LAS HERRAMIENTAS INDEPENDIENTES
│   ├── video-compressor/         # Compresor de video acelerado por GPU (AV1, HEVC, H.264)
│   │   ├── compress_video.py
│   │   ├── compress_video.bat
│   │   └── README.md
│   ├── pdf-optimizer/            # Optimizador híbrido de PDFs (OCR-Safe y Blindaje de Firmas)
│   │   ├── pdf_optimizer.py
│   │   ├── pdf_optimizer.bat
│   │   ├── requirements.txt
│   │   └── README.md
│   ├── system-backup-preformat/  # Snapshot integral y asistente post-formateo
│   │   ├── backup_preformat.ps1
│   │   ├── backup_preformat.bat
│   │   ├── template_reinstall.ps1
│   │   └── README.md
│   ├── vscode-path-doctor/       # Auditor de salud dev y reparación de PATH
│   │   ├── dev_doctor.py
│   │   ├── check_vscode_path.ps1
│   │   ├── check_vscode_path.bat
│   │   └── README.md
│   └── README.md                 # Catálogo general de herramientas
├── pyproject.toml                # Configuración de empaquetado, pytest y Ruff
├── tools.py                      # CLI central, menú TUI y despachador maestro in-process
├── tools.bat                     # Lanzador interactivo en 1 clic para Windows
├── tools.sh                      # Lanzador interactivo para Linux y macOS
├── tools.spec                    # Especificación PyInstaller para compilar binarios
├── setup.ps1                     # Provisionamiento automatizado en PowerShell
├── setup.bat                     # Acceso directo para setup en 1 clic
├── .gitattributes                # Normalización de saltos de línea (LF/CRLF)
├── .gitignore                    # Exclusiones estrictas de perfiles y temporales
├── LICENSE                       # Licencia MIT
└── README.md                     # Documentación principal
```
---

## 📜 Licencia

Distribuido bajo la Licencia MIT. Consulta el archivo [`LICENSE`](LICENSE) para más información.

**Autor:** [Klever López](https://github.com/Klopezxd) — [@Klopezxd](https://github.com/Klopezxd)
