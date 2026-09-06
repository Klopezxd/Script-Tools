# 🩺 VS Code PATH Doctor

Script de diagnóstico y reparación automática para el comando `code` de Visual Studio Code en Windows.

## 🌟 Funcionalidad
* **Detección exhaustiva:** Verifica si el comando `code` responde y si apunta al binario oficial.
* **Búsqueda inteligente:** Localiza instalaciones en `%LOCALAPPDATA%`, `Program Files` y versiones Insiders.
* **Reparación Permanente:** Opción interactiva para reinsertar automáticamente el directorio `bin` en el `PATH` del usuario en el Registro de Windows.

## 💻 Uso
```powershell
# Desde PowerShell:
.\check_vscode_path.ps1

# O doble clic sobre:
check_vscode_path.bat
```
