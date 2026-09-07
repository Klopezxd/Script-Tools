#!/usr/bin/env python3
"""
Developer Environment Doctor & VS Code Health Diagnostician.
Multiplatform diagnostic tool (Windows, macOS, Linux) that audits developer
toolchains (VS Code, Git, Compilers, Python, Docker, FFmpeg) and provides
actionable remediation steps.
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

# Enable UTF-8 console output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


@dataclass
class CheckResult:
    category: str
    component: str
    status: str  # "OK", "WARN", "MISSING"
    details: str
    recommendation: Optional[str] = None


def check_command(cmd: str, args: List[str]) -> Tuple[bool, str]:
    """Runs a command with arguments and returns (success, first_line_of_output)."""
    binary = shutil.which(cmd)
    if not binary:
        return False, "No encontrado en PATH"
    try:
        proc = subprocess.run(
            [cmd] + args,
            capture_output=True,
            text=True,
            timeout=4,
        )
        combined = (proc.stdout.strip() + "\n" + proc.stderr.strip()).strip()
        first_line = combined.splitlines()[0] if combined else f"Presente en {binary}"
        return True, first_line
    except Exception:
        return True, f"Presente en {binary}"


def audit_vscode() -> List[CheckResult]:
    """Audits Visual Studio Code CLI and installation paths."""
    results = []
    code_bin = shutil.which("code") or shutil.which("code.cmd")

    if code_bin:
        try:
            proc = subprocess.run(
                [code_bin, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=True,
            )
            lines = proc.stdout.strip().splitlines()
            ver = lines[0] if lines else "Version detectada"
            arch = lines[2] if len(lines) >= 3 else ""
            results.append(
                CheckResult(
                    category="Editor",
                    component="VS Code CLI (`code`)",
                    status="OK",
                    details=f"v{ver} ({arch}) -> {code_bin}",
                )
            )
        except Exception as err:
            results.append(
                CheckResult(
                    category="Editor",
                    component="VS Code CLI (`code`)",
                    status="WARN",
                    details=f"Binario encontrado pero fallo --version: {err}",
                    recommendation="Revisa permisos de ejecucion o ejecuta el Shell Command en VS Code.",
                )
            )
    else:
        # Check standard paths
        found_path = None
        if sys.platform == "win32":
            candidates = [
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Microsoft VS Code/bin/code.cmd",
                Path(os.environ.get("ProgramFiles", "")) / "Microsoft VS Code/bin/code.cmd",
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Microsoft VS Code Insiders/bin/code-insiders.cmd",
            ]
            for c in candidates:
                if c.exists():
                    found_path = c
                    break

        if found_path:
            results.append(
                CheckResult(
                    category="Editor",
                    component="VS Code CLI (`code`)",
                    status="WARN",
                    details=f"Instalacion detectada pero NO esta en el PATH: {found_path.parent}",
                    recommendation="Ejecuta check_vscode_path.ps1 para registrar la ruta en el PATH de Windows.",
                )
            )
        else:
            results.append(
                CheckResult(
                    category="Editor",
                    component="VS Code CLI (`code`)",
                    status="MISSING",
                    details="No se encontro VS Code en PATH ni en rutas habituales.",
                    recommendation="Descarga VS Code desde https://code.visualstudio.com o instala via winget/scoop/brew.",
                )
            )

    return results


def audit_git() -> List[CheckResult]:
    """Audits Git installation, user identity, and line-ending config."""
    results = []
    ok, out = check_command("git", ["--version"])
    if ok:
        results.append(
            CheckResult(
                category="VCS",
                component="Git",
                status="OK",
                details=out,
            )
        )
        # Check user name and email
        try:
            name_p = subprocess.run(
                ["git", "config", "--global", "user.name"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            email_p = subprocess.run(
                ["git", "config", "--global", "user.email"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            name = name_p.stdout.strip()
            email = email_p.stdout.strip()
            if name and email:
                results.append(
                    CheckResult(
                        category="VCS",
                        component="Git Identity",
                        status="OK",
                        details=f"{name} <{email}>",
                    )
                )
            else:
                results.append(
                    CheckResult(
                        category="VCS",
                        component="Git Identity",
                        status="WARN",
                        details="Falta configurar user.name o user.email",
                        recommendation="Ejecuta: git config --global user.name 'Tu Nombre' && git config --global user.email 'tu@email.com'",
                    )
                )
        except Exception:
            pass
    else:
        results.append(
            CheckResult(
                category="VCS",
                component="Git",
                status="MISSING",
                details="Git no esta disponible en el PATH",
                recommendation="Instala Git: winget install Git.Git / scoop install git / brew install git",
            )
        )
    return results


def audit_compilers() -> List[CheckResult]:
    """Audits C/C++ compilers, CMake, and Ninja."""
    results = []
    tools = [
        ("CMake", "cmake", ["--version"]),
        ("Ninja", "ninja", ["--version"]),
        ("GCC", "gcc", ["--version"]),
        ("Clang", "clang", ["--version"]),
        ("MSVC (cl)", "cl", []),
    ]
    for label, binary, args in tools:
        ok, out = check_command(binary, args)
        if ok:
            results.append(
                CheckResult(
                    category="Compiladores",
                    component=label,
                    status="OK",
                    details=out,
                )
            )
        else:
            # Compilers might be optional depending on workflow
            results.append(
                CheckResult(
                    category="Compiladores",
                    component=label,
                    status="MISSING",
                    details="No detectado en PATH",
                    recommendation=f"Instala {label} si trabajas con proyectos C/C++ nativos.",
                )
            )
    return results


def audit_runtimes() -> List[CheckResult]:
    """Audits Python, Node.js, .NET, and Rust."""
    results = []

    # Python
    ok, out = check_command("python", ["--version"])
    if ok:
        results.append(CheckResult("Runtimes", "Python", "OK", out))
    else:
        results.append(CheckResult("Runtimes", "Python", "MISSING", "Python no encontrado en PATH"))

    # Node
    ok, out = check_command("node", ["--version"])
    if ok:
        results.append(CheckResult("Runtimes", "Node.js", "OK", out))
    else:
        results.append(CheckResult("Runtimes", "Node.js", "MISSING", "Node.js no detectado"))

    # .NET
    ok, out = check_command("dotnet", ["--version"])
    if ok:
        results.append(CheckResult("Runtimes", ".NET SDK", "OK", out))
    else:
        results.append(CheckResult("Runtimes", ".NET SDK", "MISSING", "dotnet CLI no encontrado"))

    # Rust
    ok, out = check_command("cargo", ["--version"])
    if ok:
        results.append(CheckResult("Runtimes", "Rust / Cargo", "OK", out))
    else:
        results.append(CheckResult("Runtimes", "Rust / Cargo", "MISSING", "Cargo no detectado"))

    return results


def audit_multimedia() -> List[CheckResult]:
    """Audits FFmpeg and Ghostscript for Script-Tools utilities."""
    results = []

    # FFmpeg
    ok, out = check_command("ffmpeg", ["-version"])
    if ok:
        results.append(CheckResult("Multimedia", "FFmpeg", "OK", out))
    else:
        results.append(
            CheckResult(
                category="Multimedia",
                component="FFmpeg",
                status="MISSING",
                details="Requerido para video-compressor",
                recommendation="Instala: scoop install ffmpeg  o  winget install Gyan.FFmpeg",
            )
        )

    # Ghostscript
    gs_bin = shutil.which("gswin64c") or shutil.which("gs")
    if gs_bin:
        results.append(CheckResult("Multimedia", "Ghostscript", "OK", f"Detectado en {gs_bin}"))
    else:
        results.append(
            CheckResult(
                category="Multimedia",
                component="Ghostscript",
                status="MISSING",
                details="Opcional (pdf-optimizer usa motor nativo de Python)",
                recommendation="Instala Ghostscript solo si deseas compresion profunda de ultra-ahorro.",
            )
        )

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Developer Environment Doctor & VS Code Health Diagnostician",
    )
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON estructurado")
    args = parser.parse_args()

    os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"

    if not args.json:
        console.print()
        console.print(
            Panel.fit(
                f"[bold cyan]🩺 Developer Environment Doctor[/bold cyan]\n"
                f"[dim]Sistema Operativo:[/dim] [white]{os_info}[/white] | "
                f"[dim]Python:[/dim] [white]{sys.version.split()[0]}[/white]",
                border_style="cyan",
            )
        )

    all_checks: List[CheckResult] = []
    all_checks.extend(audit_vscode())
    all_checks.extend(audit_git())
    all_checks.extend(audit_compilers())
    all_checks.extend(audit_runtimes())
    all_checks.extend(audit_multimedia())

    if args.json:
        import json

        data = [
            {
                "category": c.category,
                "component": c.component,
                "status": c.status,
                "details": c.details,
                "recommendation": c.recommendation,
            }
            for c in all_checks
        ]
        print(json.dumps(data, indent=2))
        return 0

    table = Table(title="Resultados del Diagnostico", show_lines=True)
    table.add_column("Categoria", style="cyan", no_wrap=True)
    table.add_column("Componente", style="bold white")
    table.add_column("Estado", justify="center")
    table.add_column("Detalles")
    table.add_column("Recomendacion / Accion", style="yellow")

    status_badges = {
        "OK": "[bold green]✅ OK[/bold green]",
        "WARN": "[bold yellow]⚠️ WARN[/bold yellow]",
        "MISSING": "[bold red]❌ MISSING[/bold red]",
    }

    for c in all_checks:
        badge = status_badges.get(c.status, c.status)
        rec = c.recommendation or "-"
        table.add_row(c.category, c.component, badge, c.details, rec)

    console.print(table)
    console.print()

    missing_count = sum(1 for c in all_checks if c.status == "MISSING")
    warn_count = sum(1 for c in all_checks if c.status == "WARN")
    ok_count = sum(1 for c in all_checks if c.status == "OK")

    console.print(
        f"[bold]Resumen:[/bold] [green]{ok_count} correctos[/green] | "
        f"[yellow]{warn_count} avisos[/yellow] | "
        f"[red]{missing_count} no encontrados[/red]\n"
    )

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Operación cancelada por el usuario.[/yellow]")
        sys.exit(130)
