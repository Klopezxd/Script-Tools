# 💾 System Pre-Format Backup & Restore

Suite integral en PowerShell para respaldar el estado completo de un entorno de desarrollo en Windows previo a un formateo del sistema operativo, generando scripts automáticos para restaurar hasta el 95% de la configuración.

## 📋 ¿Qué respalda?
* 🐍 **Python:** Paquetes instalados (`pip freeze` para reinstalación automática).
* 🍫 **Chocolatey:** Configuración y lista de paquetes instalados (`choco export`).
* 📦 **Node.js:** Paquetes globales instalados vía `npm`.
* 🔧 **Git:** Configuración global y alias (`git config --list`).
* 💻 **Programas Instalados:** Inventario exhaustivo a través del Registro de Windows (HKLM 64-bit, HKLM 32-bit, HKCU y desinstaladores).
* ⚙️ **Compiladores:** Detección de GCC, G++, Clang y MSVC C++.
* 🌐 **Variables de Entorno:** Exportación de claves de registro del sistema y del usuario (`.reg`).
* 🐍 **Conda:** Inventario de entornos virtuales existentes.

## 📁 Archivos Generados
Al ejecutar el respaldo se crea una carpeta en el Escritorio llamada `Backup_Formateo_YYYY-MM-DD/` con:
* `REINSTALL_script.ps1`: Script PowerShell para reinstalación automatizada desatendida.
* `REINSTALL_requirements.txt`: Archivo de requisitos para `pip install -r`.
* `REINSTALL_chocolatey_packages.config`: Configuración para `choco install`.
* `REFERENCE_*.txt`: Archivos de texto con el inventario completo para consulta manual.

## 💻 Uso
```powershell
# Ejecutar como Administrador:
.\backup_preformat.ps1

# O doble clic sobre:
backup_preformat.bat
```
