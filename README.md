# Script-Tools

[![CI](https://img.shields.io/github/actions/workflow/status/Klopezxd/Script-Tools/ci.yml?branch=main&label=CI&logo=githubactions&logoColor=white&style=flat-square)](https://github.com/Klopezxd/Script-Tools/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/Klopezxd/Script-Tools?style=flat-square&logo=github&logoColor=white&label=Release)](https://github.com/Klopezxd/Script-Tools/releases)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

Colección modular de herramientas de automatización para desarrolladores: compresión multimedia acelerada por GPU, optimización de documentos con preservación estricta de OCR y auditoría integral de entornos de desarrollo.

Disponible mediante CLI unificada (`tools.py` / binario standalone), ejecución independiente por módulo o integración al menú contextual del sistema operativo.

---

## Herramientas Incluidas (`tools/`)

Todas las herramientas independientes se encuentran organizadas en el directorio [`tools/`](tools/):

| Herramienta | Directorio | Plataforma | Capacidades Principales | Ejecución Rápida |
|---|---|---|---|---|
| **Video Compressor** | [`tools/video-compressor/`](tools/video-compressor/) | Multiplataforma | Compresión multi-códec (**AV1, HEVC/H.265, H.264, VP9**), auto-detección de GPU (NVENC, VideoToolbox, QSV, AMF) y modo **Target Size a 2 pasadas** para WhatsApp y Discord. | `python tools.py video <file> --target-size 15MB` |
| **PDF Optimizer** | [`tools/pdf-optimizer/`](tools/pdf-optimizer/) | Multiplataforma | Motor híbrido con re-muestreo de imágenes en memoria y optimización de flujos de objetos. **Preservación garantizada de capas de texto y OCR**. Funciona sin dependencias externas (Ghostscript opcional). | `python tools.py pdf <file> --profile balanced` |
| **System Backup Pre-Format** | [`tools/system-backup-preformat/`](tools/system-backup-preformat/) | Windows | Snapshot integral del entorno dev (**Winget, Scoop, VS Code settings y extensiones, Git, WSL2, compiladores, variables de entorno**). Genera `REINSTALL.ps1` interactivo. | `powershell .\tools\system-backup-preformat\backup_preformat.ps1` |
| **Dev Environment Doctor** | [`tools/vscode-path-doctor/`](tools/vscode-path-doctor/) | Multiplataforma | **Dev Doctor** multiplataforma (audita salud de VS Code, Git, compiladores C/C++, CMake, Ninja, runtimes) + Reparador de PATH de VS Code en Windows. | `python tools.py doctor` |

---

## CLI Central (`tools.py`)

El despachador central en la raíz del repositorio permite ejecutar cualquier herramienta de forma unificada:

```bash
# 1. Compresión de video con límite estricto de tamaño (WhatsApp / Discord)
python tools.py video clase.mp4 --target-size 15MB

# 2. Compresión de video con aceleración por GPU y códec AV1
python tools.py video gameplay.mkv --codec av1 --preset high --resolution 1080p

# 3. Optimización de PDF manteniendo capas OCR intactas
python tools.py pdf documento.pdf --profile balanced

# 4. Auditoría de salud del entorno de desarrollo
python tools.py doctor

# 5. Respaldo de sistema Windows previo a formateo
python tools.py backup

# 6. Generador de autocompletado para el shell
python tools.py completion powershell
```

*Cada subdirectorio incluye también sus propios scripts y lanzadores para uso completamente desacoplado.*

---

## Integración al Explorador de Windows

Permite invocar las herramientas directamente desde el menú contextual de clic derecho en Windows (instalación a nivel de usuario en `HKCU`, sin requerir privilegios de Administrador):

```powershell
# Instalar accesos directos en el menú contextual:
.\scripts\install_context_menu.bat

# Desinstalar limpiamente:
.\scripts\uninstall_context_menu.bat
```

* **Videos (`.mp4`, `.mkv`, `.mov`, `.avi`, `.webm`):** Clic derecho > *"Comprimir con Script-Tools"*.
* **Documentos (`.pdf`):** Clic derecho > *"Optimizar con Script-Tools"*.

---

## Autocompletado de Terminal

Habilita autocompletado nativo para todos los subcomandos y banderas técnicas (`--codec`, `--preset`, `--target-size`, `--hwaccel`, etc.):

```powershell
# En PowerShell (agregar a $PROFILE para persistencia):
tools completion powershell | Out-String | Invoke-Expression

# En Bash:
eval "$(tools completion bash)"

# En Zsh:
source <(tools completion zsh)
```

---

## Instalación y Configuración

### Opción A: Configuración Automatizada (Windows)
Haz doble clic en **`setup.bat`** (o ejecuta desde PowerShell):
```powershell
.\setup.ps1
```
El script crea automáticamente el entorno virtual (`.venv`), actualiza `pip`, instala todas las dependencias y audita la presencia de `ffmpeg`.

### Opción B: Ejecutable Autónomo Standalone (Sin Requerir Python)
Si no deseas instalar Python ni configurar entornos virtuales, descarga el binario precompilado independiente desde [**Releases**](https://github.com/Klopezxd/Script-Tools/releases):
* **Windows:** `tools-windows-x64.exe` (puedes colocarlo en tu PATH o renombrarlo a `tools.exe`).
* **Linux:** `tools-linux-x64`.
* **macOS:** `tools-macos-universal`.

### Opción C: Instalación Manual
```bash
# 1. Clonar el repositorio
git clone https://github.com/Klopezxd/Script-Tools.git
cd Script-Tools

# 2. Instalar dependencias en tu entorno
pip install -r tools/pdf-optimizer/requirements.txt
```

---

## Suite de Pruebas y Calidad de Código

El proyecto cuenta con una suite de pruebas automatizadas unitarias y de integración en **Pytest**:

```bash
# Ejecutar suite de pruebas completa
pytest -v

# Verificar estilo y formato con Ruff
ruff check .
```

---

## Proyectos Relacionados

Para mantener la máxima cohesión técnica y aprovechar arquitecturas nativas y en la nube, los siguientes proyectos se mantienen en repositorios independientes:

* **[`whisperx-transcriptor`](https://github.com/Klopezxd/whisperx-transcriptor):** Pipeline de transcripción fonética y diarización de locutores en la nube sobre Hugging Face Spaces (ZeroGPU NVIDIA A100/T4 + Pyannote 3.1).
* **[`vet-prescription-generator`](https://github.com/Klopezxd/vet-prescription-generator):** Aplicación de escritorio nativa en **C# .NET 10** (`Single-File AOT Trimmed`, ~13 MB) con servidor HTTP embebido, SQLite WAL y generación oficial de recetas veterinarias para Agrocalidad Ecuador.

---

## Estructura del Repositorio

```text
Script-Tools/
├── .github/                      # Automatización CI/CD (Ubuntu, Windows, macOS)
├── scripts/                      # Utilidades de instalación (menú contextual Explorer)
├── tests/                        # Suite automatizada de pruebas QA (Pytest)
├── tools/                        # 👈 TODAS LAS HERRAMIENTAS INDEPENDIENTES
│   ├── video-compressor/         # Compresor de video acelerado por GPU
│   │   ├── compress_video.py
│   │   ├── compress_video.bat
│   │   └── README.md
│   ├── pdf-optimizer/            # Optimizador híbrido de PDFs (OCR-Safe)
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
├── tools.py                      # CLI central y despachador maestro in-process
├── tools.spec                    # Especificación PyInstaller para compilar binarios
├── setup.ps1                     # Provisionamiento automatizado en PowerShell
├── setup.bat                     # Acceso directo para setup en 1 clic
├── .gitattributes                # Normalización de saltos de línea (LF/CRLF)
├── .gitignore                    # Exclusiones estrictas de perfiles y temporales
├── LICENSE                       # Licencia MIT
└── README.md                     # Documentación principal
```

---

## Licencia

Distribuido bajo la Licencia MIT. Consulta el archivo [`LICENSE`](LICENSE) para más información.

**Autor:** [Klever López](https://github.com/Klopezxd) — [@Klopezxd](https://github.com/Klopezxd)
