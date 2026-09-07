# ==============================================================================
# Windows Developer Pre-Format Backup & Snapshot Suite
# Author: Klever Lopez (@Klopezxd) - Script-Tools
# Captura de forma exhaustiva el entorno de desarrollo de Windows:
# Winget, Scoop, Chocolatey, VS Code (extensiones y settings), Git, WSL2,
# Compiladores (MSVC/GCC/Clang/CMake/Ninja), Runtimes (.NET, Python, Node),
# Registro de programas y Variables de entorno.
# Genera REINSTALL.ps1 para restauracion interactiva o desatendida.
# ==============================================================================

[CmdletBinding()]
param(
    [Parameter(Position=0)]
    [string]$TargetDir = ""
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  [SCRIPT-TOOLS] WINDOWS DEV PRE-FORMAT SNAPSHOT & RESTORE SUITE" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""

$dateStr = Get-Date -Format 'yyyy-MM-dd_HH-mm'
if ([string]::IsNullOrWhiteSpace($TargetDir)) {
    $backupDir = [System.IO.Path]::Combine($env:USERPROFILE, "Desktop", "Backup_Windows_Dev_$dateStr")
} else {
    $backupDir = [System.IO.Path]::GetFullPath($TargetDir)
}
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

Write-Host "Directorio de respaldo: $backupDir" -ForegroundColor Green
Write-Host ""

# Resumen de inventario
$summary = [ordered]@{
    "Fecha" = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    "Usuario" = $env:USERNAME
    "Equipo" = $env:COMPUTERNAME
    "Winget" = "No"
    "Scoop" = "No"
    "Chocolatey" = "No"
    "Python" = "No"
    "Node" = "No"
    "VSCode_Extensiones" = 0
    "Compiladores" = @()
    "WSL_Distros" = 0
}

# ------------------------------------------------------------------------------
# 1. WINGET (Microsoft Official Windows Package Manager)
# ------------------------------------------------------------------------------
Write-Host "-> [1/11] Exportando paquetes de Winget..." -ForegroundColor Yellow
try {
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        $wingetJson = "$backupDir\REINSTALL_winget_packages.json"
        & winget export -o $wingetJson --include-versions --accept-source-agreements 2>$null
        if (Test-Path $wingetJson) {
            Write-Host "   [OK] Winget exportado a JSON oficial" -ForegroundColor Green
            $summary["Winget"] = "Si (JSON exportado)"
        } else {
            winget list > "$backupDir\REFERENCE_winget_list.txt" 2>$null
            Write-Host "   [OK] Winget listado en texto" -ForegroundColor Green
            $summary["Winget"] = "Si (Lista texto)"
        }
    } else {
        Write-Host "   [AVISO] Winget no disponible en este sistema" -ForegroundColor DarkGray
    }
} catch {
    Write-Host "   [WARN] Error con Winget: $($_.Exception.Message)" -ForegroundColor Red
}

# ------------------------------------------------------------------------------
# 2. SCOOP (Command-line installer para desarrolladores)
# ------------------------------------------------------------------------------
Write-Host "-> [2/11] Exportando aplicaciones de Scoop..." -ForegroundColor Yellow
try {
    if (Get-Command scoop -ErrorAction SilentlyContinue) {
        & scoop export > "$backupDir\REINSTALL_scoop_apps.txt" 2>$null
        & scoop bucket list > "$backupDir\REFERENCE_scoop_buckets.txt" 2>$null
        Write-Host "   [OK] Scoop apps y buckets respaldados" -ForegroundColor Green
        $summary["Scoop"] = "Si"
    } else {
        Write-Host "   [AVISO] Scoop no detectado" -ForegroundColor DarkGray
    }
} catch {
    Write-Host "   [WARN] Error con Scoop: $($_.Exception.Message)" -ForegroundColor Red
}

# ------------------------------------------------------------------------------
# 3. CHOCOLATEY
# ------------------------------------------------------------------------------
Write-Host "-> [3/11] Respaldando Chocolatey..." -ForegroundColor Yellow
try {
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        choco list > "$backupDir\REFERENCE_chocolatey_packages.txt" 2>$null
        choco export "$backupDir\REINSTALL_chocolatey_packages.config" 2>$null
        Write-Host "   [OK] Paquetes de Chocolatey exportados" -ForegroundColor Green
        $summary["Chocolatey"] = "Si"
    } else {
        Write-Host "   [AVISO] Chocolatey no detectado" -ForegroundColor DarkGray
    }
} catch {
    Write-Host "   [WARN] Error con Chocolatey: $($_.Exception.Message)" -ForegroundColor Red
}

# ------------------------------------------------------------------------------
# 4. VISUAL STUDIO CODE (Extensiones, Settings y Keybindings)
# ------------------------------------------------------------------------------
Write-Host "-> [4/11] Respaldando Visual Studio Code..." -ForegroundColor Yellow
try {
    $vscodeConfigDir = "$backupDir\VSCode_Config"
    New-Item -ItemType Directory -Path $vscodeConfigDir -Force | Out-Null

    if (Get-Command code -ErrorAction SilentlyContinue) {
        $extensions = & code --list-extensions 2>$null
        if ($extensions) {
            $extensions | Out-File "$backupDir\REINSTALL_vscode_extensions.txt" -Encoding UTF8
            $summary["VSCode_Extensiones"] = $extensions.Count
            Write-Host "   [OK] $($extensions.Count) extensiones de VS Code listadas" -ForegroundColor Green
        }
    }

    $appDataCode = "$env:APPDATA\Code\User"
    if (Test-Path "$appDataCode\settings.json") {
        Copy-Item "$appDataCode\settings.json" -Destination "$vscodeConfigDir\settings.json" -Force
        Write-Host "   [OK] settings.json respaldado" -ForegroundColor Green
    }
    if (Test-Path "$appDataCode\keybindings.json") {
        Copy-Item "$appDataCode\keybindings.json" -Destination "$vscodeConfigDir\keybindings.json" -Force
        Write-Host "   [OK] keybindings.json respaldado" -ForegroundColor Green
    }
    if (Test-Path "$appDataCode\snippets") {
        Copy-Item "$appDataCode\snippets" -Destination "$vscodeConfigDir\snippets" -Recurse -Force
        Write-Host "   [OK] Snippets personalizados respaldados" -ForegroundColor Green
    }
} catch {
    Write-Host "   [WARN] Error con VS Code: $($_.Exception.Message)" -ForegroundColor Red
}

# ------------------------------------------------------------------------------
# 5. PYTHON Y PIP
# ------------------------------------------------------------------------------
Write-Host "-> [5/11] Respaldando entorno Python y pip..." -ForegroundColor Yellow
try {
    if (Get-Command pip -ErrorAction SilentlyContinue) {
        pip list > "$backupDir\REFERENCE_pip_packages.txt" 2>$null
        pip freeze > "$backupDir\REINSTALL_requirements.txt" 2>$null
        $pyVer = & python --version 2>$null
        Write-Host "   [OK] Python respaldado ($pyVer)" -ForegroundColor Green
        $summary["Python"] = "$pyVer"
    } else {
        Write-Host "   [AVISO] Python/pip no detectado en PATH" -ForegroundColor DarkGray
    }
} catch {
    Write-Host "   [WARN] Error con Python: $($_.Exception.Message)" -ForegroundColor Red
}

# ------------------------------------------------------------------------------
# 6. NODE.JS Y NPM
# ------------------------------------------------------------------------------
Write-Host "-> [6/11] Respaldando Node.js y paquetes globales de npm..." -ForegroundColor Yellow
try {
    if (Get-Command npm -ErrorAction SilentlyContinue) {
        npm list -g --depth=0 > "$backupDir\REFERENCE_npm_packages.txt" 2>$null
        $nodeVer = & node --version 2>$null
        Write-Host "   [OK] Node.js respaldado ($nodeVer)" -ForegroundColor Green
        $summary["Node"] = "$nodeVer"
    } else {
        Write-Host "   [AVISO] Node.js no detectado" -ForegroundColor DarkGray
    }
} catch {
    Write-Host "   [WARN] Error con Node.js: $($_.Exception.Message)" -ForegroundColor Red
}

# ------------------------------------------------------------------------------
# 7. TOOLCHAIN C/C++, CMAKE, NINJA, RUST Y .NET
# ------------------------------------------------------------------------------
Write-Host "-> [7/11] Auditando compiladores y SDKs (C/C++, CMake, Ninja, .NET, Rust)..." -ForegroundColor Yellow
try {
    $compilersFound = @()
    if (Get-Command cl -ErrorAction SilentlyContinue) { $compilersFound += "MSVC C++ (cl.exe)" }
    if (Get-Command gcc -ErrorAction SilentlyContinue) { $compilersFound += "GCC" }
    if (Get-Command g++ -ErrorAction SilentlyContinue) { $compilersFound += "G++" }
    if (Get-Command clang -ErrorAction SilentlyContinue) { $compilersFound += "Clang" }
    if (Get-Command cmake -ErrorAction SilentlyContinue) {
        $cmakeVer = (& cmake --version | Select-Object -First 1)
        $compilersFound += "CMake ($cmakeVer)"
    }
    if (Get-Command ninja -ErrorAction SilentlyContinue) { $compilersFound += "Ninja Build" }
    if (Get-Command dotnet -ErrorAction SilentlyContinue) {
        $dotnetSdks = & dotnet --list-sdks 2>$null
        $dotnetSdks | Out-File "$backupDir\REFERENCE_dotnet_sdks.txt"
        $compilersFound += ".NET SDKs"
    }
    if (Get-Command cargo -ErrorAction SilentlyContinue) { $compilersFound += "Rust / Cargo" }

    if ($compilersFound.Count -gt 0) {
        $compilersFound | Out-File "$backupDir\REFERENCE_compilers_installed.txt" -Encoding UTF8
        Write-Host "   [OK] Herramientas detectadas: $($compilersFound -join ', ')" -ForegroundColor Green
        $summary["Compiladores"] = $compilersFound
    } else {
        Write-Host "   [AVISO] No se detectaron compiladores de linea de comandos" -ForegroundColor DarkGray
    }
} catch {
    Write-Host "   [WARN] Error auditando compiladores: $($_.Exception.Message)" -ForegroundColor Red
}

# ------------------------------------------------------------------------------
# 8. GIT Y TERMINAL / SHELL PROFILE
# ------------------------------------------------------------------------------
Write-Host "-> [8/11] Respaldando configuracion de Git y perfiles de terminal..." -ForegroundColor Yellow
try {
    if (Get-Command git -ErrorAction SilentlyContinue) {
        git config --list --global > "$backupDir\REINSTALL_git_config.txt" 2>$null
        Write-Host "   [OK] Git config global respaldada" -ForegroundColor Green
    }

    # Perfil PowerShell
    if (Test-Path $PROFILE) {
        Copy-Item $PROFILE -Destination "$backupDir\powershell_profile.ps1" -Force
        Write-Host "   [OK] Perfil PowerShell respaldado" -ForegroundColor Green
    }

    # Auditoria de llaves SSH (Solo publicas, con advertencia de seguridad)
    $sshDir = "$env:USERPROFILE\.ssh"
    if (Test-Path $sshDir) {
        $pubKeys = Get-ChildItem -Path $sshDir -Filter "*.pub" -ErrorAction SilentlyContinue
        if ($pubKeys) {
            $pubDir = "$backupDir\SSH_Public_Keys"
            New-Item -ItemType Directory -Path $pubDir -Force | Out-Null
            $pubKeys | Copy-Item -Destination $pubDir -Force
            Write-Host "   [OK] Claves publicas SSH respaldadas en $pubDir" -ForegroundColor Green
        }
        $secLines = @(
            "[RECORDATORIO DE SEGURIDAD CRITICO]",
            "Se detectaron llaves privadas o credenciales en $sshDir.",
            "Por razones de seguridad estricta, NUNCA se copian llaves privadas automaticamente.",
            "-> Respalda tus archivos id_rsa o id_ed25519 a una memoria USB cifrada antes de formatear."
        )
        $secLines | Out-File "$backupDir\AVISO_IMPORTANTE_LLAVES_SSH.txt" -Encoding UTF8
    }
} catch {
    Write-Host "   [WARN] Error con Git/Terminal: $($_.Exception.Message)" -ForegroundColor Red
}

# ------------------------------------------------------------------------------
# 9. WSL 2 DISTRIBUCIONES
# ------------------------------------------------------------------------------
Write-Host "-> [9/11] Comprobando distribuciones de WSL 2..." -ForegroundColor Yellow
try {
    if (Get-Command wsl -ErrorAction SilentlyContinue) {
        $wslList = & wsl --list --verbose 2>$null
        if ($wslList) {
            $wslList | Out-File "$backupDir\REFERENCE_wsl_distributions.txt" -Encoding UTF8
            Write-Host "   [OK] Distribuciones de WSL 2 catalogadas" -ForegroundColor Green
            $summary["WSL_Distros"] = "Detectadas"
        }
    }
} catch {
    Write-Host "   [WARN] Error consultando WSL: $($_.Exception.Message)" -ForegroundColor Red
}

# ------------------------------------------------------------------------------
# 10. VARIABLES DE ENTORNO Y REGISTRO
# ------------------------------------------------------------------------------
Write-Host "-> [10/11] Exportando variables de entorno del sistema y usuario..." -ForegroundColor Yellow
try {
    reg export "HKEY_CURRENT_USER\Environment" "$backupDir\REFERENCE_user_env_vars.reg" /y 2>$null
    reg export "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "$backupDir\REFERENCE_system_env_vars.reg" /y 2>$null
    Write-Host "   [OK] Claves de registro de variables exportadas (.reg)" -ForegroundColor Green
} catch {
    Write-Host "   [WARN] Error exportando variables de entorno: $($_.Exception.Message)" -ForegroundColor Red
}

# ------------------------------------------------------------------------------
# 11. INVENTARIO COMPLETO DE PROGRAMAS INSTALADOS (HKLM + HKCU)
# ------------------------------------------------------------------------------
Write-Host "-> [11/11] Generando inventario exhaustivo de programas instalados..." -ForegroundColor Yellow
try {
    $allPrograms = @()

    $hklm64 = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue |
        Where-Object {$_.DisplayName} |
        Select-Object @{N="Name";E={$_.DisplayName}}, @{N="Version";E={if($_.DisplayVersion){$_.DisplayVersion}else{"Unknown"}}}, @{N="Publisher";E={if($_.Publisher){$_.Publisher}else{"Unknown"}}}, @{N="Source";E={"Registry-HKLM64"}}
    $allPrograms += $hklm64

    $hklm32 = Get-ItemProperty HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue |
        Where-Object {$_.DisplayName} |
        Select-Object @{N="Name";E={$_.DisplayName}}, @{N="Version";E={if($_.DisplayVersion){$_.DisplayVersion}else{"Unknown"}}}, @{N="Publisher";E={if($_.Publisher){$_.Publisher}else{"Unknown"}}}, @{N="Source";E={"Registry-HKLM32"}}
    $allPrograms += $hklm32

    $hkcu = Get-ItemProperty HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue |
        Where-Object {$_.DisplayName} |
        Select-Object @{N="Name";E={$_.DisplayName}}, @{N="Version";E={if($_.DisplayVersion){$_.DisplayVersion}else{"Unknown"}}}, @{N="Publisher";E={if($_.Publisher){$_.Publisher}else{"Unknown"}}}, @{N="Source";E={"Registry-HKCU"}}
    $allPrograms += $hkcu

    # Deduplicar
    $unique = $allPrograms | Sort-Object Name -Unique
    $formattedList = $unique | Format-Table -AutoSize | Out-String
    $formattedList | Out-File "$backupDir\REFERENCE_programas_instalados_COMPLETO.txt" -Encoding UTF8
    Write-Host "   [OK] $($unique.Count) aplicaciones registradas en inventario completo" -ForegroundColor Green
} catch {
    Write-Host "   [WARN] Error listando programas: $($_.Exception.Message)" -ForegroundColor Red
}

# ------------------------------------------------------------------------------
# GENERADOR DEL SCRIPT DE REINSTALACION AUTOMATICA (REINSTALL.ps1)
# ------------------------------------------------------------------------------
Write-Host ""
Write-Host "-> Generando instalador interactivo post-formateo (REINSTALL.ps1)..." -ForegroundColor Cyan
$templateFile = Join-Path $PSScriptRoot "template_reinstall.ps1"
if (Test-Path $templateFile) {
    Copy-Item $templateFile -Destination "$backupDir\REINSTALL.ps1" -Force
    Write-Host "   [OK] REINSTALL.ps1 generado exitosamente desde plantilla" -ForegroundColor Green
}

# ------------------------------------------------------------------------------
# GENERADOR DEL REPORTE EJECUTIVO EN MARKDOWN (SYSTEM_INVENTORY.md)
# ------------------------------------------------------------------------------
$invFile = Join-Path $backupDir "SYSTEM_INVENTORY.md"
$compText = if ($summary["Compiladores"].Count -gt 0) { $summary["Compiladores"] -join ", " } else { "No detectados" }
$sb = New-Object System.Text.StringBuilder
[void]$sb.AppendLine("# Snapshot de Entorno de Desarrollo Windows")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("- Fecha de Respaldo: " + $summary["Fecha"])
[void]$sb.AppendLine("- Usuario: " + $summary["Usuario"])
[void]$sb.AppendLine("- Equipo: " + $summary["Equipo"])
[void]$sb.AppendLine("")
[void]$sb.AppendLine("---")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("## Toolchain de Desarrollo")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("- Winget: " + $summary["Winget"])
[void]$sb.AppendLine("- Scoop: " + $summary["Scoop"])
[void]$sb.AppendLine("- Chocolatey: " + $summary["Chocolatey"])
[void]$sb.AppendLine("- VS Code Extensiones: " + $summary["VSCode_Extensiones"])
[void]$sb.AppendLine("- Python: " + $summary["Python"])
[void]$sb.AppendLine("- Node.js: " + $summary["Node"])
[void]$sb.AppendLine("- Compiladores: " + $compText)
[void]$sb.AppendLine("- WSL 2: " + $summary["WSL_Distros"])
[void]$sb.AppendLine("")
[void]$sb.AppendLine("---")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("## Instrucciones de Restauracion")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("1. Copia esta carpeta completa a tu equipo recien formateado.")
[void]$sb.AppendLine("2. Abre PowerShell como Administrador en esta carpeta.")
[void]$sb.AppendLine("3. Ejecuta: .\REINSTALL.ps1")
[void]$sb.AppendLine("4. Elige que herramientas deseas restaurar interactivamente.")
[System.IO.File]::WriteAllText($invFile, $sb.ToString(), [System.Text.Encoding]::UTF8)
Write-Host "   [OK] SYSTEM_INVENTORY.md generado exitosamente" -ForegroundColor Green

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Green
Write-Host "  [EXITO] RESPALDO PRE-FORMATEO COMPLETADO" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
Write-Host "Ubicacion: $backupDir" -ForegroundColor Cyan
Write-Host "Recuerda copiar esta carpeta a un almacenamiento externo (USB/SSD)" -ForegroundColor Yellow
Write-Host ""

try {
    Start-Process explorer $backupDir
} catch {}