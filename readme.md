# 🛠️ Script-Tools: Windows Automation & Developer Toolkit

![OS](https://img.shields.io/badge/OS-Windows%2010%20%2F%2011-0078D6.svg?logo=windows&logoColor=white)
![PowerShell](https://img.shields.io/badge/Shell-PowerShell%205.1%2B-5391FE.svg?logo=powershell&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB.svg?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Code Style](https://img.shields.io/badge/Code%20Style-Clean%20Code-brightgreen.svg)

> **Colección curada y modular de utilidades de automatización, optimización multimedia y mantenimiento de sistema para entornos de desarrollo en Windows.**

---

## 🧰 Utilidades Incluidas

| Herramienta | Área | Tecnologías | Descripción | Ejecución Rápida |
|---|---|---|---|---|
| **[`video-compressor/`](video-compressor/)** | Multimedia | PowerShell, FFmpeg | Compresión eficiente con códec H.265 (HEVC) reduciendo peso hasta 80%. Soporta drag & drop. | Arrastrar sobre `compress_video.bat` |
| **[`pdf-optimizer/`](pdf-optimizer/)** | Documentos | Python, Ghostscript, pikepdf, PyMuPDF | Reducción de tamaño en 3 niveles preservando texto seleccionable y capas OCR. | `python pdf_optimizer.py` |
| **[`system-backup-preformat/`](system-backup-preformat/)** | SysAdmin | PowerShell, Windows Registry | Respaldo total previo a formateo (pip, npm, choco, env vars, git) con script de reinstalación automática. | `backup_preformat.bat` |
| **[`vscode-path-doctor/`](vscode-path-doctor/)** | Diagnóstico | PowerShell | Diagnóstico de integración de VS Code y reparación automática del comando `code` en el PATH. | `check_vscode_path.bat` |

---

## 🚀 Proyectos Especializados Independientes

Para mantener la cohesión arquitectónica y permitir integración con plataformas en la nube, los siguientes proyectos han sido migrados a sus propios repositorios especializados:

* 🎙️ **[`whisperx-transcriptor`](https://github.com/Klopezxd/whisperx-transcriptor):** Pipeline de transcripción fonética precisa y diarización de hablantes con aceleración CUDA.
  * *Demo en vivo en la nube:* [![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/Klopezxd/transcriptor-whisperx)
* 🐾 **[`vet-prescription-generator`](https://github.com/Klopezxd/vet-prescription-generator):** Sistema de escritorio en Tkinter para generación secuencial de recetas médicas veterinarias en Word y PDF.

---

## 💻 Requisitos Globales del Sistema

* **Sistema Operativo:** Windows 10 u 11 (64-bit).
* **PowerShell:** Versión 5.1 o PowerShell 7+.
* **Python:** 3.8+ (necesario para las herramientas basadas en Python).
* **FFmpeg:** Instalado en el sistema y registrado en el PATH (para compresión de video).
* **Ghostscript:** Instalado en el sistema (para optimización de PDF).

---

## 📁 Estructura del Repositorio

```text
Script-Tools/
├── video-compressor/
│   ├── compress_video.ps1       # Script de compresión H.265
│   ├── compress_video.bat       # Lanzador drag & drop / selector gráfico
│   └── readme.md
├── pdf-optimizer/
│   ├── pdf_optimizer.py         # Optimizador inteligente de PDFs
│   ├── requirements.txt         # Dependencias Python
│   └── readme.md
├── system-backup-preformat/
│   ├── backup_preformat.ps1     # Extractor del estado del sistema
│   ├── backup_preformat.bat     # Lanzador automatizado con permisos
│   └── readme.md
├── vscode-path-doctor/
│   ├── check_vscode_path.ps1    # Diagnóstico y reparación de PATH
│   ├── check_vscode_path.bat    # Lanzador con diagnóstico interactivo
│   └── readme.md
├── .gitignore                   # Exclusión estricta de temporales y perfiles privados
├── LICENSE                      # Licencia MIT
└── README.md                    # Documentación principal
```

---

## 📄 Licencia

Distribuido bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

**Autor:** [Klever López](https://github.com/Klopezxd)
