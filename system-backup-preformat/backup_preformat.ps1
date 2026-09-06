# Script de respaldo completo antes de formatear
# Ejecutar como administrador

$backupDir = "$env:USERPROFILE\Desktop\Backup_Formateo_$(Get-Date -Format 'yyyy-MM-dd')"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

Write-Host "Creando respaldo en: $backupDir" -ForegroundColor Green
Write-Host ""

# 1. Paquetes de Python
Write-Host "-> Respaldando paquetes de Python..." -ForegroundColor Yellow
try {
    if (Get-Command pip -ErrorAction SilentlyContinue) {
        pip list > "$backupDir\REFERENCE_pip_packages.txt" 2>$null
        pip freeze > "$backupDir\REINSTALL_requirements.txt" 2>$null
        Write-Host "[OK] Paquetes de Python respaldados" -ForegroundColor Green
    } else {
        "Python/pip no instalado" | Out-File "$backupDir\REFERENCE_pip_packages.txt"
        Write-Host "[AVISO] Python/pip no encontrado" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[ERROR] Error con Python: $($_.Exception.Message)" -ForegroundColor Red
}

# 2. Compiladores C/C++
Write-Host "-> Verificando compiladores C/C++..." -ForegroundColor Yellow
try {
    $compilers = @()
    if (Get-Command cl -ErrorAction SilentlyContinue) { $compilers += "Visual Studio C++" }
    if (Get-Command gcc -ErrorAction SilentlyContinue) { $compilers += "GCC" }
    if (Get-Command g++ -ErrorAction SilentlyContinue) { $compilers += "G++" }
    if (Get-Command clang -ErrorAction SilentlyContinue) { $compilers += "Clang" }

    if ($compilers.Count -gt 0) {
        $compilers | Out-File "$backupDir\REFERENCE_compilers_installed.txt"
        Write-Host "[OK] Compiladores: $($compilers -join ', ')" -ForegroundColor Green
    } else {
        "No se encontraron compiladores C/C++" | Out-File "$backupDir\REFERENCE_compilers_installed.txt"
        Write-Host "[AVISO] No se encontraron compiladores" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[ERROR] Error con compiladores: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Chocolatey
Write-Host "-> Respaldando Chocolatey..." -ForegroundColor Yellow
try {
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        choco list > "$backupDir\REFERENCE_chocolatey_packages.txt" 2>$null
        choco export "$backupDir\REINSTALL_chocolatey_packages.config" 2>$null
        Write-Host "[OK] Paquetes de Chocolatey respaldados" -ForegroundColor Green
    } else {
        "Chocolatey no instalado" | Out-File "$backupDir\REFERENCE_chocolatey_packages.txt"
        Write-Host "[AVISO] Chocolatey no encontrado" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[ERROR] Error con Chocolatey: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. Variables de entorno
Write-Host "-> Respaldando variables de entorno..." -ForegroundColor Yellow
try {
    reg export "HKEY_CURRENT_USER\Environment" "$backupDir\REFERENCE_user_env_vars.reg" /y 2>$null
    reg export "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "$backupDir\REFERENCE_system_env_vars.reg" /y 2>$null
    Write-Host "[OK] Variables de entorno exportadas" -ForegroundColor Green
    Write-Host "[IMPORTANTE] Usar SOLO como referencia" -ForegroundColor Red
} catch {
    Write-Host "[ERROR] Error con variables de entorno: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. PROGRAMAS INSTALADOS
Write-Host "-> Listando TODOS los programas instalados..." -ForegroundColor Yellow
try {
    $allPrograms = @()

    # Fuente 1: Registro HKLM (64-bit)
    Write-Host "  Buscando en registro HKLM 64-bit..." -ForegroundColor Cyan
    try {
        $programs1 = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue |
            Where-Object {$_.DisplayName -ne $null -and $_.DisplayName.Trim() -ne ""} |
            Select-Object @{Name="Name"; Expression={$_.DisplayName}},
                         @{Name="Version"; Expression={if($_.DisplayVersion){$_.DisplayVersion}else{"Unknown"}}},
                         @{Name="Publisher"; Expression={if($_.Publisher){$_.Publisher}else{"Unknown"}}},
                         @{Name="Source"; Expression={"Registry-HKLM"}}
        $allPrograms += $programs1
    } catch {}

    # Fuente 2: Registro HKLM Wow6432Node (32-bit en 64-bit)
    Write-Host "  Buscando en registro HKLM 32-bit..." -ForegroundColor Cyan
    try {
        $programs2 = Get-ItemProperty HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue |
            Where-Object {$_.DisplayName -ne $null -and $_.DisplayName.Trim() -ne ""} |
            Select-Object @{Name="Name"; Expression={$_.DisplayName}},
                         @{Name="Version"; Expression={if($_.DisplayVersion){$_.DisplayVersion}else{"Unknown"}}},
                         @{Name="Publisher"; Expression={if($_.Publisher){$_.Publisher}else{"Unknown"}}},
                         @{Name="Source"; Expression={"Registry-HKLM-32bit"}}
        $allPrograms += $programs2
    } catch {}

    # Fuente 3: Registro HKCU (usuario actual)
    Write-Host "  Buscando en registro HKCU..." -ForegroundColor Cyan
    try {
        $programs3 = Get-ItemProperty HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue |
            Where-Object {$_.DisplayName -ne $null -and $_.DisplayName.Trim() -ne ""} |
            Select-Object @{Name="Name"; Expression={$_.DisplayName}},
                         @{Name="Version"; Expression={if($_.DisplayVersion){$_.DisplayVersion}else{"Unknown"}}},
                         @{Name="Publisher"; Expression={if($_.Publisher){$_.Publisher}else{"Unknown"}}},
                         @{Name="Source"; Expression={"Registry-HKCU"}}
        $allPrograms += $programs3
    } catch {}

    # Fuente 4: Microsoft Store Apps (con manejo de errores mejorado)
    Write-Host "  Buscando aplicaciones de Microsoft Store..." -ForegroundColor Cyan
    try {
        # Intentar primero sin -AllUsers para evitar errores de permisos
        $storeApps = @()
        try {
            $storeApps = Get-AppxPackage -ErrorAction SilentlyContinue |
                Where-Object {$_.Name -notlike "Microsoft.Windows*" -and $_.Name -notlike "windows.*" -and $_.Name -ne $null} |
                Select-Object @{Name="Name"; Expression={$_.Name}},
                             @{Name="Version"; Expression={$_.Version}},
                             @{Name="Publisher"; Expression={$_.Publisher}},
                             @{Name="Source"; Expression={"Microsoft Store"}}
        } catch {
            # Si falla, intentar con -AllUsers solo si se ejecuta como administrador
            if (([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
                try {
                    $storeApps = Get-AppxPackage -AllUsers -ErrorAction SilentlyContinue |
                        Where-Object {$_.Name -notlike "Microsoft.Windows*" -and $_.Name -notlike "windows.*" -and $_.Name -ne $null} |
                        Select-Object @{Name="Name"; Expression={$_.Name}},
                                     @{Name="Version"; Expression={$_.Version}},
                                     @{Name="Publisher"; Expression={$_.Publisher}},
                                     @{Name="Source"; Expression={"Microsoft Store"}}
                } catch {
                    Write-Host "    [AVISO] No se pudieron obtener apps de Microsoft Store" -ForegroundColor Yellow
                }
            } else {
                Write-Host "    [AVISO] Permisos limitados para Microsoft Store apps" -ForegroundColor Yellow
            }
        }
        $allPrograms += $storeApps
    } catch {}

    # Fuente 5: WinGet (si esta disponible)
    Write-Host "  Buscando con WinGet..." -ForegroundColor Cyan
    try {
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            $wingetOutput = winget list 2>$null
            if ($wingetOutput) {
                $wingetLines = $wingetOutput | Where-Object {$_ -match '\S' -and $_ -notmatch '^Name\s+Id\s+Version' -and $_ -notmatch '^-+'}
                foreach ($line in $wingetLines) {
                    if ($line -match '(.+?)\s+([A-Za-z0-9\.\-_]+\.[A-Za-z0-9\.\-_]+)\s+(.+)$') {
                        $wingetProgram = [PSCustomObject]@{
                            Name = $matches[1].Trim()
                            Version = $matches[3].Trim()
                            Publisher = "WinGet Package"
                            Source = "WinGet"
                        }
                        $allPrograms += $wingetProgram
                    }
                }
            }
        }
    } catch {}

    # Eliminar duplicados y valores nulos
    Write-Host "  Eliminando duplicados..." -ForegroundColor Cyan
    $uniquePrograms = @{}
    $finalPrograms = @()

    foreach ($program in $allPrograms) {
        # Verificar que el programa y su nombre no sean nulos
        if ($program -ne $null -and $program.Name -ne $null -and $program.Name.Trim() -ne "") {
            $key = $program.Name.ToLower().Trim()
            if (-not $uniquePrograms.ContainsKey($key)) {
                $uniquePrograms[$key] = $true
                $finalPrograms += $program
            }
        }
    }

    # Ordenar por nombre
    $finalPrograms = $finalPrograms | Sort-Object Name

    # Crear formato de salida
    $output = @()
    $output += "PROGRAMAS INSTALADOS - RESPALDO COMPLETO"
    $output += "========================================"
    $output += "Total de programas encontrados: $($finalPrograms.Count)"
    $output += "Fuentes consultadas: Registry HKLM, Registry HKLM-32bit, Registry HKCU, Microsoft Store, WinGet"
    $output += ""
    $output += "Package                                    Version              Publisher                        Source"
    $output += "------------------------------------------ -------------------- -------------------------------- ----------------"

    foreach ($program in $finalPrograms) {
        $name = if ($program.Name.Length -gt 42) { $program.Name.Substring(0, 39) + "..." } else { $program.Name }
        $version = if ($program.Version.Length -gt 20) { $program.Version.Substring(0, 17) + "..." } else { $program.Version }
        $publisher = if ($program.Publisher.Length -gt 32) { $program.Publisher.Substring(0, 29) + "..." } else { $program.Publisher }
        $source = if ($program.Source.Length -gt 16) { $program.Source.Substring(0, 13) + "..." } else { $program.Source }

        $line = $name.PadRight(42) + " " + $version.PadRight(20) + " " + $publisher.PadRight(32) + " " + $source
        $output += $line
    }

    $output | Out-File "$backupDir\REFERENCE_programas_instalados_COMPLETO.txt" -Encoding UTF8
    Write-Host "[OK] Lista COMPLETA de programas exportada ($($finalPrograms.Count) programas encontrados)" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Error listando programas: $($_.Exception.Message)" -ForegroundColor Red
}

# 6. Git
Write-Host "-> Respaldando Git..." -ForegroundColor Yellow
try {
    if (Get-Command git -ErrorAction SilentlyContinue) {
        git config --list --global > "$backupDir\REINSTALL_git_config.txt" 2>$null
        Write-Host "[OK] Git respaldado" -ForegroundColor Green
    } else {
        "Git no instalado" | Out-File "$backupDir\REFERENCE_git_config.txt"
        Write-Host "[AVISO] Git no encontrado" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[ERROR] Error con Git: $($_.Exception.Message)" -ForegroundColor Red
}

# 7. Node.js y npm
Write-Host "-> Respaldando Node.js..." -ForegroundColor Yellow
try {
    if (Get-Command npm -ErrorAction SilentlyContinue) {
        npm list -g --depth=0 > "$backupDir\REINSTALL_npm_packages.txt" 2>$null
        node --version > "$backupDir\REFERENCE_node_version.txt" 2>$null
        Write-Host "[OK] Node.js respaldado" -ForegroundColor Green
    } else {
        "Node.js no instalado" | Out-File "$backupDir\REFERENCE_npm_packages.txt"
        Write-Host "[AVISO] Node.js no encontrado" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[ERROR] Error con Node.js: $($_.Exception.Message)" -ForegroundColor Red
}

# 8. Conda
Write-Host "-> Listando Conda..." -ForegroundColor Yellow
try {
    if (Get-Command conda -ErrorAction SilentlyContinue) {
        conda env list > "$backupDir\REFERENCE_conda_environments.txt" 2>$null
        Write-Host "[OK] Conda listado" -ForegroundColor Green
    } else {
        "Conda no instalado" | Out-File "$backupDir\REFERENCE_conda_environments.txt"
        Write-Host "[AVISO] Conda no encontrado" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[ERROR] Error con Conda: $($_.Exception.Message)" -ForegroundColor Red
}

# 9. VS Code
Write-Host "-> Verificando VS Code..." -ForegroundColor Yellow
try {
    if (Get-Command code -ErrorAction SilentlyContinue) {
        "VS Code instalado - Se sincroniza automaticamente con tu cuenta Microsoft" | Out-File "$backupDir\REFERENCE_vscode_info.txt"
        Write-Host "[OK] VS Code detectado - Se sincroniza automaticamente" -ForegroundColor Green
        Write-Host "[INFO] No necesitas respaldar extensiones ni configuracion" -ForegroundColor Cyan
    } else {
        "VS Code no instalado" | Out-File "$backupDir\REFERENCE_vscode_info.txt"
        Write-Host "[AVISO] VS Code no encontrado" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[ERROR] Error verificando VS Code: $($_.Exception.Message)" -ForegroundColor Red
}

# 10. Informacion del sistema
Write-Host "-> Recopilando informacion del sistema..." -ForegroundColor Yellow
try {
    systeminfo > "$backupDir\REFERENCE_system_info.txt" 2>$null
    Get-ComputerInfo | Out-File "$backupDir\REFERENCE_computer_info.txt"
    Write-Host "[OK] Informacion guardada" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Error con informacion del sistema: $($_.Exception.Message)" -ForegroundColor Red
}

# Crear script de reinstalacion
Write-Host "Creando script de reinstalacion..." -ForegroundColor Yellow
$reinstallScript = @"
# Script de reinstalacion post-formateo
# Ejecutar como administrador

Write-Host "=== REINSTALACION POST-FORMATEO ===" -ForegroundColor Green

# 1. Chocolatey
if (Test-Path "REINSTALL_chocolatey_packages.config") {
    Write-Host "-> Instalando Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

    Write-Host "-> Reinstalando paquetes de Chocolatey..." -ForegroundColor Yellow
    choco install REINSTALL_chocolatey_packages.config -y
    Write-Host "[OK] Chocolatey reinstalado" -ForegroundColor Green
} else {
    Write-Host "[AVISO] No se encontro REINSTALL_chocolatey_packages.config" -ForegroundColor Yellow
}

# 2. Python packages
if (Test-Path "REINSTALL_requirements.txt") {
    Write-Host "-> Reinstalando Python packages..." -ForegroundColor Yellow
    pip install -r REINSTALL_requirements.txt
    Write-Host "[OK] Python packages reinstalados" -ForegroundColor Green
} else {
    Write-Host "[AVISO] No se encontro REINSTALL_requirements.txt" -ForegroundColor Yellow
}

# 3. Git configuracion automatica
if (Test-Path "REINSTALL_git_config.txt") {
    Write-Host "-> Configurando Git automaticamente..." -ForegroundColor Yellow

    # Leer el archivo de configuracion de Git
    `$gitConfig = Get-Content "REINSTALL_git_config.txt"

    foreach (`$line in `$gitConfig) {
        if (`$line -match "^user\.name=(.+)") {
            `$userName = `$matches[1]
            git config --global user.name "`$userName"
            Write-Host "  - Nombre configurado: `$userName" -ForegroundColor Cyan
        }
        elseif (`$line -match "^user\.email=(.+)") {
            `$userEmail = `$matches[1]
            git config --global user.email "`$userEmail"
            Write-Host "  - Email configurado: `$userEmail" -ForegroundColor Cyan
        }
        elseif (`$line -match "^core\.editor=(.+)") {
            `$editor = `$matches[1]
            git config --global core.editor "`$editor"
            Write-Host "  - Editor configurado: `$editor" -ForegroundColor Cyan
        }
    }

    Write-Host "[OK] Git configurado automaticamente" -ForegroundColor Green
} else {
    Write-Host "[AVISO] No se encontro REINSTALL_git_config.txt" -ForegroundColor Yellow
}

# 4. Node.js packages globales
if (Test-Path "REINSTALL_npm_packages.txt") {
    Write-Host "-> Reinstalando paquetes globales de Node.js..." -ForegroundColor Yellow

    # Leer el archivo y extraer nombres de paquetes
    `$npmContent = Get-Content "REINSTALL_npm_packages.txt"
    foreach (`$line in `$npmContent) {
        if (`$line -match '^\+-- (.+?)@') {
            `$packageName = `$matches[1]
            if (`$packageName -ne "npm") {  # Evitar reinstalar npm
                Write-Host "  - Instalando: `$packageName" -ForegroundColor Cyan
                npm install -g `$packageName
            }
        }
    }

    Write-Host "[OK] Paquetes globales de Node.js reinstalados" -ForegroundColor Green
} else {
    Write-Host "[AVISO] No se encontro REINSTALL_npm_packages.txt" -ForegroundColor Yellow
}

# 5. VS Code (se sincroniza automaticamente)
Write-Host "[INFO] VS Code se sincroniza automaticamente con tu cuenta Microsoft" -ForegroundColor Cyan
Write-Host "       Solo necesitas hacer login en VS Code" -ForegroundColor Cyan

Write-Host ""
Write-Host "=== REVISAR MANUALMENTE ===" -ForegroundColor Yellow
Write-Host "- Variables de entorno (archivos REFERENCE_*.reg) - SOLO como referencia"
Write-Host "- Lista COMPLETA de programas (REFERENCE_programas_instalados_COMPLETO.txt)"
Write-Host "- Informacion del sistema para referencia"
Write-Host ""
Write-Host "[COMPLETADO] Reinstalacion automatica terminada" -ForegroundColor Green
"@

$reinstallScript | Out-File "$backupDir\REINSTALL_script.ps1"
Write-Host "[OK] Script de reinstalacion creado" -ForegroundColor Green

# Crear README
$readme = @"
RESPALDO PRE-FORMATEO - INSTRUCCIONES

ARCHIVOS PARA REINSTALACION AUTOMATICA (REINSTALL_):
- REINSTALL_requirements.txt -> Paquetes Python (se reinstalan automaticamente)
- REINSTALL_chocolatey_packages.config -> Paquetes Chocolatey (se reinstalan automaticamente)
- REINSTALL_git_config.txt -> Configuracion Git (se configura automaticamente)
- REINSTALL_npm_packages.txt -> Paquetes globales Node.js (se reinstalan automaticamente)
- REINSTALL_script.ps1 -> SCRIPT PRINCIPAL DE REINSTALACION

ARCHIVOS DE REFERENCIA (REFERENCE_):
- REFERENCE_programas_instalados_COMPLETO.txt -> Lista COMPLETA de TODOS los programas
- REFERENCE_vscode_info.txt -> Info VS Code (se sincroniza automaticamente)
- REFERENCE_system_info.txt -> Informacion del sistema
- REFERENCE_computer_info.txt -> Informacion detallada del equipo
- REFERENCE_user_env_vars.reg -> Variables de entorno usuario (solo referencia)
- REFERENCE_system_env_vars.reg -> Variables de entorno sistema (solo referencia)
- REFERENCE_compilers_installed.txt -> Compiladores detectados
- REFERENCE_conda_environments.txt -> Entornos de Conda
- REFERENCE_node_version.txt -> Version de Node.js

COMO USAR DESPUES DE FORMATEAR:
1. Instalar Windows y drivers basicos
2. Ejecutar como administrador: .\REINSTALL_script.ps1
3. El script hara TODO automaticamente:
   - Instala Chocolatey y sus paquetes
   - Reinstala paquetes de Python
   - Configura Git con tu nombre y email
   - Reinstala paquetes globales de Node.js
4. Para VS Code: solo hacer login (se sincroniza solo)
5. Revisar REFERENCE_programas_instalados_COMPLETO.txt para instalar manualmente otros programas

IMPORTANTE:
- El 95% se hace automaticamente con REINSTALL_script.ps1
- VS Code se sincroniza automaticamente con tu cuenta Microsoft
- Los archivos REFERENCE_ son solo para consulta
- Solo necesitas revisar manualmente las variables de entorno si es necesario
"@

$readme | Out-File "$backupDir\README.txt"

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "RESPALDO COMPLETADO" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host "Ubicacion: $backupDir" -ForegroundColor Cyan
Write-Host "Copiar a USB antes de formatear" -ForegroundColor Yellow

# Abrir carpeta
try {
    Start-Process explorer $backupDir
    Write-Host "[OK] Carpeta abierta" -ForegroundColor Green
} catch {
    Write-Host "[AVISO] Abrir manualmente: $backupDir" -ForegroundColor Yellow
}