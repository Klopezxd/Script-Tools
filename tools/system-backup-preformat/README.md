# System Backup Pre-Format Suite

Suite de auditoría, respaldo y restauración integral diseñada para entornos de desarrollo en Windows previo a un formateo del sistema operativo. Captura el ecosistema de herramientas de desarrollo (Winget, Scoop, VS Code, Git, WSL2, compiladores y variables de entorno) y genera un asistente interactivo (`REINSTALL.ps1`) para restaurar el entorno post-formateo.

---

## Componentes Respaldados

* **Winget:** Exportación oficial en formato JSON (`winget export`) para reinstalación desatendida.
* **Scoop:** Aplicaciones instaladas y buckets activos (`scoop export`).
* **Chocolatey:** Paquetes instalados (`REINSTALL_chocolatey_packages.config`).
* **Visual Studio Code:**
  * Lista completa de extensiones instaladas (`code --list-extensions`).
  * Respaldo directo de configuraciones de usuario (`settings.json`, `keybindings.json` y snippets).
* **Compiladores y Toolchain:** Detección de MSVC (`cl.exe`), GCC, G++, Clang, CMake, Ninja, .NET SDKs y Rust/Cargo.
* **WSL 2:** Auditoría de distribuciones de Linux activas (`wsl -l -v`).
* **Git y Terminal:** Configuración global (`~/.gitconfig`), perfil de PowerShell (`$PROFILE`) y advertencia de seguridad para respaldar llaves SSH privadas.
* **Python y Node:** Lista de paquetes globales (`pip freeze`, `npm list -g`).
* **Variables de Entorno:** Claves de registro completas del sistema y de usuario (`.reg`).
* **Inventario General:** Lista de programas instalados en HKLM (64 y 32 bits) y HKCU deduplicados.

---

## Estructura del Respaldo Generado

El script crea una carpeta en tu Escritorio (`Backup_Windows_Dev_YYYY-MM-DD_HH-mm/`) conteniendo:

```text
Backup_Windows_Dev_2026-09-07_13-00/
├── REINSTALL.ps1                         # Asistente interactivo para restaurar todo
├── SYSTEM_INVENTORY.md                   # Resumen ejecutivo de hardware y toolchain
├── REINSTALL_winget_packages.json        # Paquetes Winget listos para 'winget import'
├── REINSTALL_scoop_apps.txt              # Aplicaciones de Scoop listas para reinstalar
├── REINSTALL_vscode_extensions.txt       # Extensiones de VS Code
├── REINSTALL_requirements.txt            # Dependencias pip de Python
├── REINSTALL_git_config.txt              # Ajustes globales de Git
├── VSCode_Config/                        # Copia de settings.json y snippets
├── SSH_Public_Keys/                      # Llaves publicas (.pub)
├── REFERENCE_compilers_installed.txt     # Compiladores y versiones
├── REFERENCE_wsl_distributions.txt       # Distribuciones de WSL 2
├── REFERENCE_programas_instalados.txt    # Inventario completo de software
└── REFERENCE_*_env_vars.reg              # Variables de entorno exportadas
```

---

## Flujo de Trabajo

### Paso 1: Generar el Respaldo (Antes de Formatear)

Puedes ejecutar el respaldo mediante cualquiera de estas 3 vías:
```powershell
# Opción A: Desde la CLI unificada en la raíz
python tools.py backup

# Opción B: Ejecución directa en PowerShell
powershell -NoProfile -ExecutionPolicy Bypass -File .\backup_preformat.ps1

# Opción C: Doble clic en Windows Explorer
backup_preformat.bat
```

> [!IMPORTANT]
> **Checklist de Seguridad y Discos Externos:**
> 1. Copia la carpeta generada en el Escritorio (`Backup_Windows_Dev_*`) a una unidad USB o disco externo.
> 2. Por seguridad criptográfica, el script **NUNCA** copia tus llaves SSH privadas (`id_rsa`, `id_ed25519`). Respalda manualmente tu carpeta `~/.ssh` de forma encriptada si la necesitas.

### Paso 2: Restaurar en el Sistema Limpio (Post-Formateo)

1. Conecta tu disco o memoria USB al equipo recién formateado.
2. Abre una terminal de PowerShell dentro de la carpeta del respaldo.
3. Ejecuta el asistente interactivo:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\REINSTALL.ps1
   ```
4. El asistente presentará un menú interactivo para instalar desatendidamente:
   * Paquetes de **Winget**
   * Aplicaciones de **Scoop** y sus buckets
   * Extensiones y configuraciones de **VS Code**
   * Configuración global de **Git**
   * Paquetes globales de **Python (pip)**

