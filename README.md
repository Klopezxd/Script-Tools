# 🛠️ Script-Tools: Multiplatform Developer & Automation Toolkit

[![CI Status](https://img.shields.io/badge/CI-GitHub%20Actions%20Passing-brightgreen.svg?logo=githubactions&logoColor=white)](https://github.com/Klopezxd/Script-Tools)
[![OS - Multiplatform](https://img.shields.io/badge/OS-Windows%20%7C%20Linux%20%7C%20macOS-0078D6.svg?logo=windows&logoColor=white)](https://github.com/Klopezxd/Script-Tools)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![Code Style](https://img.shields.io/badge/Code%20Style-Ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Tests](https://img.shields.io/badge/QA%20Tests-42%20Passed-brightgreen.svg)](tests/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Colección modular de herramientas de automatización, compresión multimedia acelerada por GPU, optimización de documentos preservando OCR y auditoría de entornos de desarrollo.**
> Diseñado bajo arquitectura desacoplada: utilizable tanto mediante una **CLI unificada central (`tools.py` / `tools.exe`)** como de forma **independiente por módulo**, con integración nativa al **Explorador de Windows**.

---

## 🧰 Utilidades Incluidas

| Módulo | Alcance | Tecnologías Clave | Capacidades Principales | Ejecución Rápida |
|---|---|---|---|---|
| **[`video-compressor/`](video-compressor/)** | Multiplataforma | Python 3.10+, FFmpeg, GPU HWAccel | Compresión multi-códec (**AV1, HEVC/H.265, H.264, VP9**), auto-detección de GPU (NVENC, VideoToolbox, QSV, AMF) y modo **Target Size a 2 pasadas** para WhatsApp/Discord. | `python tools.py video <file> --target-size 15MB` |
| **[`pdf-optimizer/`](pdf-optimizer/)** | Multiplataforma | Python, PyMuPDF, pikepdf, Pillow | Motor híbrido con re-muestreo de imágenes en memoria y optimización de flujos de objetos. **Garantía de 100% de preservación de texto y OCR**. Funciona sin requerir Ghostscript. | `python tools.py pdf <file> --profile balanced` |
| **[`system-backup-preformat/`](system-backup-preformat/)** | Windows Dev | PowerShell 5.1/7+, Registry, Winget, Scoop | Snapshot integral del entorno dev (**Winget, Scoop, VS Code settings y extensiones, Git, WSL2, compiladores, variables**). Genera `REINSTALL.ps1` interactivo. | `powershell .\backup_preformat.ps1` |
| **[`vscode-path-doctor/`](vscode-path-doctor/)** | Multiplataforma | Python, PowerShell, Windows Registry | **Dev Doctor** multiplataforma (audita salud de VS Code, Git, compiladores C/C++, CMake, Ninja, Runtimes) + Reparador de PATH de VS Code en Windows. | `python tools.py doctor` |

---

## 🚀 CLI Central Unificada (`tools.py`)

Puedes utilizar el orquestador principal en la raíz del repositorio para invocar cualquier herramienta:

```bash
# 1. Compresión de video con límite estricto de tamaño (ideal para WhatsApp / Discord)
python tools.py video clase.mp4 --target-size 15MB

# 2. Compresión de video con aceleración por GPU y códec moderno AV1
python tools.py video gameplay.mkv --codec av1 --preset high --resolution 1080p

# 3. Optimización de PDF manteniendo capas OCR intactas
python tools.py pdf documento.pdf --profile balanced

# 4. Auditoría de salud del entorno de desarrollo
python tools.py doctor

# 5. Respaldo de sistema Windows previo a formateo
python tools.py backup

# 6. Generador de auto-completado para tu shell favorito
python tools.py completion powershell
```

*Cada subdirectorio incluye también sus propios scripts y lanzadores para uso completamente aislado.*

---

## 🖱️ Integración al Explorador de Windows (Menú Contextual)

Para la máxima comodidad en el día a día, puedes integrar `Script-Tools` directamente al menú contextual de clic derecho en Windows (sin requerir permisos de Administrador):

```powershell
# Instalar accesos directos de clic derecho (doble clic en Explorer):
.\scripts\install_context_menu.bat

# Desinstalar limpiamente en cualquier momento:
.\scripts\uninstall_context_menu.bat
```

* **Videos (`.mp4`, `.mkv`, `.mov`, `.avi`, `.webm`, etc.):** Clic derecho > *"Comprimir con Script-Tools"*.
* **Documentos (`.pdf`):** Clic derecho > *"Optimizar con Script-Tools"*.

---

## ⚡ Autocompletado de Terminal (Tab Completion)

Habilita autocompletado nativo para todos los subcomandos y banderas técnicas (`--codec`, `--preset`, `--target-size`, `--hwaccel`, etc.):

```powershell
# En PowerShell (agrega a tu $PROFILE para persistencia):
tools completion powershell | Out-String | Invoke-Expression

# En Bash:
eval "$(tools completion bash)"

# En Zsh:
source <(tools completion zsh)
```

---

## 💻 Instalación y Configuración Rápida

### Opción A: Configuración Automatizada en 1 Clic (Recomendada en Windows)
Haz doble clic en **`setup.bat`** (o ejecuta desde PowerShell):
```powershell
.\setup.ps1
```
El script creará automáticamente el entorno virtual (`.venv`), actualizará `pip`, instalará todas las dependencias y auditará la presencia de `ffmpeg`.

### Opción B: Ejecutable Autónomo Standalone (Sin Requerir Python)
Si no deseas instalar Python ni configurar entornos virtuales, ve a la sección de [**Releases**](https://github.com/Klopezxd/Script-Tools/releases) y descarga el binario precompilado independiente:
* **Windows:** `tools-windows-x64.exe` (puedes colocarlo en tu PATH o renombrarlo a `tools.exe`).
* **Linux:** `tools-linux-x64`.
* **macOS:** `tools-macos-universal`.

### Opción C: Instalación Manual
```bash
# 1. Clonar el repositorio
git clone https://github.com/Klopezxd/Script-Tools.git
cd Script-Tools

# 2. Instalar dependencias en tu entorno
pip install -r pdf-optimizer/requirements.txt
```

---

## 🧪 Pruebas Automatizadas y Calidad de Código (QA)

El proyecto cuenta con una suite de **39 pruebas automatizadas** unitarias y de integración en **Pytest**:

```bash
# Ejecutar suite de pruebas completa
pytest -v

# Verificar estilo y formato con Ruff
ruff check .
```

---

## 🌐 Proyectos Especializados Desacoplados

Para mantener la máxima cohesión técnica y aprovechar arquitecturas nativas y en la nube, los siguientes proyectos han sido trasladados a sus propios repositorios independientes:

* 🎙️ **[`whisperx-transcriptor`](https://github.com/Klopezxd/whisperx-transcriptor):** Pipeline de transcripción fonética y diarización de locutores 100% cloud en Hugging Face Spaces (ZeroGPU NVIDIA A100/T4 + Pyannote 3.1).
* 🐾 **[`vet-prescription-generator`](https://github.com/Klopezxd/vet-prescription-generator):** Aplicación de escritorio nativa en **C# .NET 10** (`Single-File AOT Trimmed`, ~13 MB) con servidor HTTP embebido, SQLite WAL y generación oficial de recetas veterinarias para Agrocalidad Ecuador.

---

## 📁 Estructura del Repositorio

```text
Script-Tools/
├── .github/
│   └── workflows/
│       ├── ci.yml                     # Pipeline CI/CD (Ubuntu, Windows, macOS)
│       └── release.yml                # Compilación automatizada de binarios para Releases
├── scripts/
│   ├── install_context_menu.ps1       # Instalador de menú contextual (HKCU, sin Admin)
│   ├── install_context_menu.bat       # Lanzador 1-clic para instalar menú contextual
│   ├── uninstall_context_menu.ps1     # Desinstalador limpio de menú contextual
│   └── uninstall_context_menu.bat     # Lanzador 1-clic para desinstalar menú contextual
├── video-compressor/
│   ├── compress_video.py              # Compresor multi-códec y acelerado por GPU
│   ├── compress_video.bat             # Lanzador Drag & Drop para Windows
│   └── README.md                      # Documentación y recetas de compresión
├── pdf-optimizer/
│   ├── pdf_optimizer.py               # Optimizador híbrido de PDFs (Pillow + pikepdf + PyMuPDF)
│   ├── pdf_optimizer.bat              # Lanzador Drag & Drop para Windows
│   ├── requirements.txt               # Dependencias del optimizador
│   └── README.md                      # Documentación y tabla de perfiles DPI
├── system-backup-preformat/
│   ├── backup_preformat.ps1           # Snapshot integral del entorno dev en Windows
│   ├── backup_preformat.bat           # Lanzador automatizado con elevación
│   ├── template_reinstall.ps1         # Plantilla del asistente interactivo de restauración
│   └── README.md                      # Flujo de trabajo antes y después de formatear
├── vscode-path-doctor/
│   ├── dev_doctor.py                  # Auditor de salud dev multiplataforma (C++, Git, VS Code)
│   ├── check_vscode_path.ps1          # Diagnóstico y saneamiento de PATH en Windows
│   ├── check_vscode_path.bat          # Lanzador interactivo
│   └── README.md                      # Diagnóstico del toolchain de desarrollo
├── tests/
│   ├── __init__.py
│   ├── test_tools_cli.py              # Pruebas de la CLI unificada, flags y auto-completado
│   ├── test_video_compressor.py       # Pruebas del compresor y lógica de bitrate 2-pass
│   ├── test_pdf_optimizer.py          # Pruebas de OCR y compresión E2E
│   ├── test_dev_doctor.py             # Pruebas de auditoría y serialización JSON
│   └── test_powershell_scripts.py     # Validación de sintaxis AST y ejecución de PowerShell
├── pyproject.toml                     # Configuración de empaquetado, pytest y Ruff
├── tools.py                           # CLI central y despachador maestro in-process
├── tools.spec                         # Especificación PyInstaller para compilar binarios
├── setup.ps1                          # Provisionamiento automatizado en PowerShell
├── setup.bat                          # Acceso directo para setup en 1 clic
├── .gitattributes                     # Normalización de saltos de línea (LF/CRLF)
├── .gitignore                         # Exclusiones estrictas de perfiles y temporales
├── LICENSE                            # Licencia MIT
└── README.md                          # Documentación principal
```

---

## 📄 Licencia

Distribuido bajo la Licencia MIT. Consulta el archivo `LICENSE` para más información.

**Autor:** [Klever López](https://github.com/Klopezxd) — [@Klopezxd](https://github.com/Klopezxd)
