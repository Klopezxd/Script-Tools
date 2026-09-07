# Herramientas de Script-Tools (`tools/`)

Este directorio contiene los módulos y herramientas que componen la suite **Script-Tools**. Cada herramienta puede utilizarse de forma 100% desacoplada o a través de la CLI unificada central en la raíz (`tools.py`).

| Herramienta | Plataforma | Motor / Tecnologías | Descripción Breve | CLI Unificada |
|---|---|---|---|---|
| **[`video-compressor/`](video-compressor/)** | Multiplataforma | Python, FFmpeg, GPU HWAccel | Compresión multi-códec (AV1, HEVC, H.264, VP9) con aceleración por hardware y modo Target Size (WhatsApp / Discord). | `python tools.py video <file>` |
| **[`pdf-optimizer/`](pdf-optimizer/)** | Multiplataforma | Python, PyMuPDF, pikepdf, Pillow | Optimización de PDFs con preservación estricta de capas OCR y re-muestreo inteligente sin dependencias externas. | `python tools.py pdf <file>` |
| **[`system-backup-preformat/`](system-backup-preformat/)** | Windows | PowerShell 5.1/7+, Winget, Scoop, Reg | Snapshot integral del entorno dev (paquetes, extensiones, runtimes, variables) y asistente de restauración post-formateo. | `python tools.py backup` |
| **[`vscode-path-doctor/`](vscode-path-doctor/)** | Multiplataforma | Python, PowerShell, Reg | Auditoría de salud de compiladores (C++, Git, runtimes) y diagnóstico / auto-reparación del comando `code` en Windows. | `python tools.py doctor` |
