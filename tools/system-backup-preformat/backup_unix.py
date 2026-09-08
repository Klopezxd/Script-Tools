"""Multiplatform developer environment snapshot for Linux and macOS."""

from __future__ import annotations

import datetime
import shutil
import subprocess
import sys
from pathlib import Path


def backup_unix() -> int:
    """Performs developer environment backup on macOS and Linux systems."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    home = Path.home()
    desktop = home / "Desktop"
    backup_dir = (desktop if desktop.exists() else home) / f"Backup_Dev_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[INFO] Creando respaldo de desarrollo en: {backup_dir}")

    # 1. VS Code extensions
    if shutil.which("code"):
        try:
            exts = subprocess.check_output(["code", "--list-extensions"], text=True, errors="replace")
            (backup_dir / "vscode_extensions.txt").write_text(exts, encoding="utf-8")
            print("  [OK] Extensiones de VS Code exportadas.")
        except Exception as e:
            print(f"  [AVISO] No se pudieron exportar extensiones de VS Code: {e}")

    # 2. VS Code settings
    vscode_config = (
        home / "Library" / "Application Support" / "Code" / "User"
        if sys.platform == "darwin"
        else home / ".config" / "Code" / "User"
    )
    if vscode_config.exists():
        dest_vscode = backup_dir / "vscode_config"
        dest_vscode.mkdir(exist_ok=True)
        for fname in ["settings.json", "keybindings.json", "snippets"]:
            src = vscode_config / fname
            if src.is_file():
                shutil.copy2(src, dest_vscode / fname)
            elif src.is_dir():
                shutil.copytree(src, dest_vscode / fname, dirs_exist_ok=True)
        print("  [OK] Configuración y atajos de VS Code respaldados.")

    # 3. Git config
    gitconfig = home / ".gitconfig"
    if gitconfig.exists():
        shutil.copy2(gitconfig, backup_dir / ".gitconfig")
        print("  [OK] Configuración global de Git (.gitconfig) respaldada.")

    # 4. Shell configs
    shell_dest = backup_dir / "shell_configs"
    shell_dest.mkdir(exist_ok=True)
    for sfile in [".zshrc", ".bashrc", ".bash_profile", ".profile"]:
        src = home / sfile
        if src.exists():
            shutil.copy2(src, shell_dest / sfile)
    print("  [OK] Archivos de perfil de shell respaldados.")

    # 5. SSH public keys and configs (safe, no private keys)
    ssh_dir = home / ".ssh"
    if ssh_dir.exists():
        dest_ssh = backup_dir / "ssh_public"
        dest_ssh.mkdir(exist_ok=True)
        for f in ssh_dir.glob("*.pub"):
            shutil.copy2(f, dest_ssh / f.name)
        for f in ["config", "known_hosts"]:
            if (ssh_dir / f).exists():
                shutil.copy2(ssh_dir / f, dest_ssh / f)
        print("  [OK] Llaves públicas SSH y configuración respaldadas.")

    # 6. Package managers
    if sys.platform == "darwin":
        if shutil.which("brew"):
            try:
                brew_dump = subprocess.check_output(["brew", "bundle", "dump", "--file=-"], text=True, errors="replace")
                (backup_dir / "Brewfile").write_text(brew_dump, encoding="utf-8")
                print("  [OK] Paquetes y Casks de Homebrew exportados a Brewfile.")
            except Exception:
                pass
    else:
        # Linux package managers
        if shutil.which("dpkg"):
            try:
                pkgs = subprocess.check_output(["dpkg", "--get-selections"], text=True, errors="replace").splitlines()
                (backup_dir / "apt_packages.txt").write_text("\n".join(pkgs), encoding="utf-8")
                print("  [OK] Paquetes APT (Debian/Ubuntu) respaldados.")
            except Exception:
                pass
        if shutil.which("pacman"):
            try:
                pkgs = subprocess.check_output(["pacman", "-Qqe"], text=True, errors="replace").splitlines()
                (backup_dir / "pacman_packages.txt").write_text("\n".join(pkgs), encoding="utf-8")
                print("  [OK] Paquetes Pacman (Arch Linux) respaldados.")
            except Exception:
                pass
        if shutil.which("flatpak"):
            try:
                flatpaks = subprocess.check_output(
                    ["flatpak", "list", "--columns=application"],
                    text=True,
                    errors="replace",
                )
                (backup_dir / "flatpak_apps.txt").write_text(flatpaks, encoding="utf-8")
                print("  [OK] Aplicaciones Flatpak respaldadas.")
            except Exception:
                pass

    # 7. Generate restore script
    restore_sh = backup_dir / "restore.sh"
    restore_sh_content = """#!/usr/bin/env bash
# Script-Tools Automated Developer Environment Restoration
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "=== Restaurando entorno de desarrollo ==="

# 1. VS Code extensions
if command -v code >/dev/null 2>&1 && [ -f "$DIR/vscode_extensions.txt" ]; then
    echo "Instalando extensiones de VS Code..."
    while IFS= read -r ext || [ -n "$ext" ]; do
        [ -n "$ext" ] && code --install-extension "$ext" --force
    done < "$DIR/vscode_extensions.txt"
fi

# 2. VS Code config
if [ -d "$DIR/vscode_config" ]; then
    if [ "$(uname)" = "Darwin" ]; then
        DEST="$HOME/Library/Application Support/Code/User"
    else
        DEST="$HOME/.config/Code/User"
    fi
    mkdir -p "$DEST"
    cp -r "$DIR/vscode_config/"* "$DEST/"
    echo "Configuraciones de VS Code restauradas."
fi

# 3. Git config
if [ -f "$DIR/.gitconfig" ]; then
    cp "$DIR/.gitconfig" "$HOME/.gitconfig"
    echo "Git config restaurado."
fi

# 4. Homebrew
if command -v brew >/dev/null 2>&1 && [ -f "$DIR/Brewfile" ]; then
    echo "Restaurando paquetes Homebrew..."
    brew bundle --file="$DIR/Brewfile"
fi

echo "=== Restauración completada exitosamente ==="
"""
    restore_sh.write_text(restore_sh_content, encoding="utf-8")
    try:
        restore_sh.chmod(0o755)
    except Exception:
        pass

    print(f"\n[EXITO] Respaldo completado en: {backup_dir}")
    print(f"       Script de restauración generado en: {restore_sh}\n")
    return 0
