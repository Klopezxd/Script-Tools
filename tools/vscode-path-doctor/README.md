# VS Code & Dev Environment Doctor

Diagnóstico de salud integral del entorno de desarrollo y resolución de incidencias para Visual Studio Code y toolchains de programación (Git, compiladores C/C++, CMake, Ninja, .NET, Python, Node y herramientas multimedia).

---

## Funcionalidades

1. **Dev Doctor Multiplataforma (`dev_doctor.py`):**
   * Audita la disponibilidad, versión y ruta de:
     * **Editores:** Visual Studio Code CLI (`code`), Insiders y arquitectura detectada.
     * **Control de Versiones:** Git, identidad del usuario (`user.name`, `user.email`).
     * **Compiladores y Build Systems:** CMake, Ninja, GCC, Clang, MSVC (`cl.exe`).
     * **Runtimes de Desarrollo:** Python, Node.js, .NET SDK y Rust/Cargo.
     * **Multimedia de Automatización:** FFmpeg y Ghostscript.
   * Emite una tabla formateada con recomendaciones de instalación precisas por gestor de paquetes (`scoop`, `winget`, `brew`, `apt`).
   * Soporta salida en JSON estructurado para auditorías (`--json`).

2. **VS Code PATH Doctor para Windows (`check_vscode_path.ps1`):**
   * Detecta si el comando `code` responde correctamente en la consola de Windows.
   * Localiza automáticamente la carpeta `bin` de VS Code en `%LOCALAPPDATA%` o `Program Files`.
   * Permite reinsertar la ruta permanentemente en la variable `PATH` del Registro de Windows del usuario sin requerir permisos de administrador.

---

## Modos de Uso

### 1. Auditoría del Toolchain (Multiplataforma)
```bash
# Vía CLI unificada (raíz)
python tools.py doctor

# Directo en terminal (muestra tabla enriquecida en color)
python dev_doctor.py

# Exportar auditoría estructurada a JSON (ideal para CI/CD y scripts)
python dev_doctor.py --json
```

### 2. Diagnóstico y Auto-Reparación de PATH de VS Code (Windows)
Si al escribir `code .` en tu consola recibes `'code' no se reconoce como un comando interno o externo`:
```powershell
# En PowerShell interactivo:
powershell -ExecutionPolicy Bypass -File .\check_vscode_path.ps1

# En PowerShell desatendido con auto-reparación automática:
powershell -ExecutionPolicy Bypass -File .\check_vscode_path.ps1 -AutoFix -NonInteractive

# O doble clic en el archivo por lotes:
check_vscode_path.bat
```
El script localizará automáticamente tu instalación de VS Code y reescribirá la entrada faltante en `HKCU:\Environment\PATH` notificando al subsistema de Windows (`WM_SETTINGCHANGE`) para que tome efecto inmediato sin reiniciar la computadora. Con `-AutoFix`, la reparación se aplica silenciosamente sin esperar confirmación interactiva.

---

## Componentes Auditados por Dev Doctor

| Categoría | Binarios y Entornos Comprobados | Acciones Correctivas Sugeridas |
|---|---|---|
| **Editores** | Visual Studio Code (`code`), VS Code Insiders (`code-insiders`) | Comprueba ruta, binario en PATH e integridad de CLI. |
| **Control de Versiones** | Git (`git`), identidad configurada (`user.name`, `user.email`) | Verifica instalación y alerta si falta configurar autor en commits. |
| **Compiladores C/C++** | Clang (`clang`), GCC (`gcc`), G++ (`g++`), MSVC (`cl.exe`) | Audita toolchain nativo para desarrollo de sistemas y backend. |
| **Build Systems** | CMake (`cmake`), Ninja (`ninja`) | Verifica herramientas esenciales para compilar proyectos nativos. |
| **Runtimes** | Python (`python3`/`python`), Node.js (`node`), .NET SDK (`dotnet`), Rust (`rustc`, `cargo`) | Detecta versiones activas para desarrollo moderno. |
| **Multimedia** | FFmpeg (`ffmpeg`, `ffprobe`), Ghostscript (`gswin64c`/`gs`) | Audita motores de aceleración multimedia para `Script-Tools`. |

