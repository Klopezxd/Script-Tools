#!/usr/bin/env python3
"""
Script-Tools Unified CLI - Master Dispatcher.
Unified entry point for video compression, PDF optimization, and developer environment diagnostics.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

console = Console()

# Enable UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

ROOT_DIR = Path(__file__).resolve().parent

# Ensure sub-packages are discoverable
for subdir in ["video-compressor", "pdf-optimizer", "vscode-path-doctor", "system-backup-preformat"]:
    path_str = str(ROOT_DIR / "tools" / subdir)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)


def dispatch_video(extra_args: list[str]) -> int:
    """Dispatches video compression module directly in-process."""
    import compress_video

    sys.argv = ["tools video"] + extra_args
    return compress_video.main()


def dispatch_pdf(extra_args: list[str]) -> int:
    """Dispatches PDF optimization module directly in-process."""
    import pdf_optimizer

    sys.argv = ["tools pdf"] + extra_args
    return pdf_optimizer.main()


def dispatch_doctor(extra_args: list[str]) -> int:
    """Dispatches dev environment diagnostics directly in-process."""
    import dev_doctor

    sys.argv = ["tools doctor"] + extra_args
    return dev_doctor.main()


POWERSHELL_COMPLETION = """
Register-ArgumentCompleter -Native -CommandName @('tools', 'tools.exe', 'python', 'python.exe') -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    $rawTokens = $commandAst.ToString().Trim().Split(' ', [System.StringSplitOptions]::RemoveEmptyEntries)
    $tokens = @()
    for ($i = 0; $i -lt $rawTokens.Count; $i++) {
        $t = $rawTokens[$i]
        if ($t -match 'python(\\.exe)?$' -and ($i + 1 -lt $rawTokens.Count) -and ($rawTokens[$i+1] -match 'tools(\\.py)?$')) {
            $tokens += "tools"
            $i++
            continue
        }
        $tokens += $t
    }

    $subcommands = @('video', 'pdf', 'doctor', 'backup', 'completion')

    if ($tokens.Count -le 1 -or ($tokens.Count -eq 2 -and $wordToComplete -ne '')) {
        $subcommands | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
        }
        return
    }

    $sub = $tokens[1]
    if ($sub -eq 'video') {
        $opts = @('--codec', '--preset', '--resolution', '--target-size', '--hwaccel', '--crf', '--audio', '--audio-bitrate', '--speed', '--batch', '--help')
        $opts | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterName', $_)
        }
    } elseif ($sub -eq 'pdf') {
        $opts = @('--profile', '--engine', '--strict-ocr', '--batch', '--output', '--help')
        $opts | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterName', $_)
        }
    } elseif ($sub -eq 'doctor') {
        $opts = @('--json', '--help')
        $opts | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterName', $_)
        }
    } elseif ($sub -eq 'completion') {
        $shells = @('powershell', 'bash', 'zsh')
        $shells | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
        }
    }
}
"""

BASH_COMPLETION = """
_tools_completion() {
    local cur prev subcmd
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    if [ "$COMP_CWORD" -eq 1 ]; then
        COMPREPLY=( $(compgen -W "video pdf doctor backup completion --help --version" -- "$cur") )
        return 0
    fi

    subcmd="${COMP_WORDS[1]}"
    case "$subcmd" in
        video)
            COMPREPLY=( $(compgen -W "--codec --preset --resolution --target-size --hwaccel --crf --audio --audio-bitrate --speed --batch --help" -- "$cur") )
            ;;
        pdf)
            COMPREPLY=( $(compgen -W "--profile --engine --strict-ocr --batch --output --help" -- "$cur") )
            ;;
        doctor)
            COMPREPLY=( $(compgen -W "--json --help" -- "$cur") )
            ;;
        completion)
            COMPREPLY=( $(compgen -W "powershell bash zsh" -- "$cur") )
            ;;
        *)
            ;;
    esac
}
complete -F _tools_completion tools tools.exe
"""

ZSH_COMPLETION = """
#compdef tools tools.exe

_tools() {
    local -a subcommands
    subcommands=(
        'video:Comprime videos con aceleracion por hardware y multi-codec'
        'pdf:Optimiza documentos PDF preservando OCR'
        'doctor:Diagnostica la salud de VS Code y entorno dev'
        'backup:Respaldo integral pre-formateo para Windows'
        'completion:Genera scripts de autocompletado para terminales'
    )

    if (( CURRENT == 2 )); then
        _describe -t commands 'subcommand' subcommands
        return
    fi

    case $words[2] in
        video)
            _arguments \\
                '--codec[Target video codec]:codec:(hevc h264 av1 vp9)' \\
                '--preset[Quality profile]:preset:(archival high balanced draft)' \\
                '--resolution[Target resolution]:resolution:(keep 1080p 720p 480p 360p)' \\
                '--target-size[Target size constraint (e.g. 15MB)]:' \\
                '--hwaccel[Hardware acceleration]:hwaccel:(auto cpu nvenc videotoolbox qsv amf)' \\
                '--audio[Audio mode]:audio:(aac copy opus mute)' \\
                '--batch[Batch process directory]' \\
                '--help[Show help]'
            ;;
        pdf)
            _arguments \\
                '--profile[Optimization profile]:profile:(lossless print balanced screen)' \\
                '--engine[Engine to use]:engine:(native gs)' \\
                '--strict-ocr[Preserve text layer strictly]' \\
                '--batch[Batch process directory]' \\
                '--output[Output file path]:file:_files' \\
                '--help[Show help]'
            ;;
        doctor)
            _arguments \\
                '--json[Output diagnostic results as JSON]' \\
                '--help[Show help]'
            ;;
        completion)
            _arguments \\
                '1:shell:(powershell bash zsh)'
            ;;
    esac
}

_tools "$@"
"""


def dispatch_completion(extra_args: list[str]) -> int:
    """Emits auto-completion definitions for various shells."""
    if any(arg in ("-h", "--help") for arg in extra_args):
        print(
            "Uso: tools completion [powershell|bash|zsh]\n\n"
            "Genera scripts de autocompletado de argumentos para la terminal seleccionada.\n\n"
            "Instalación rápida:\n"
            "  PowerShell: tools completion powershell | Out-String | Invoke-Expression\n"
            '  Bash:       eval "$(tools completion bash)"\n'
            "  Zsh:        source <(tools completion zsh)"
        )
        return 0

    shell = extra_args[0].lower() if extra_args else "powershell"
    if shell in ("powershell", "pwsh"):
        print(POWERSHELL_COMPLETION.strip())
    elif shell == "bash":
        print(BASH_COMPLETION.strip())
    elif shell == "zsh":
        print(ZSH_COMPLETION.strip())
    else:
        sys.stderr.write(f"[ERROR] Shell no soportado: '{shell}'. Opciones válidas: powershell, bash, zsh\n")
        return 1
    return 0


def dispatch_backup(extra_args: list[str]) -> int:
    """Dispatches developer environment backup across Windows, Linux, and macOS."""
    if sys.platform == "win32":
        script = ROOT_DIR / "tools" / "system-backup-preformat" / "backup_preformat.ps1"
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)] + extra_args
        try:
            return subprocess.run(cmd).returncode
        except FileNotFoundError:
            sys.stderr.write("[ERROR] 'powershell' no está disponible en el PATH del sistema.\n")
            return 1
    else:
        import backup_unix

        return backup_unix.backup_unix()


def _interactive_video():
    console.print()
    console.print(
        Panel(
            "[bold cyan]🎥  Compresor de Video Multicódec & Aceleración GPU[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED,
        )
    )

    import shutil

    if not shutil.which("ffmpeg"):
        install_cmd = "winget install Gyan.FFmpeg"
        if sys.platform == "darwin":
            install_cmd = "brew install ffmpeg"
        elif sys.platform.startswith("linux"):
            install_cmd = "sudo apt install ffmpeg  (o sudo pacman -S ffmpeg / dnf install ffmpeg)"

        console.print(
            Panel(
                "[bold red]FFmpeg no está instalado en el sistema.[/bold red]\n\n"
                "El compresor requiere FFmpeg en el PATH para procesar y codificar video.\n\n"
                f"Comando de instalación recomendado:\n  [bold cyan]{install_cmd}[/bold cyan]",
                title="[bold yellow]Dependencia Requerida: FFmpeg[/bold yellow]",
                border_style="red",
                box=box.ROUNDED,
            )
        )
        if sys.platform == "win32" and shutil.which("winget"):
            if Confirm.ask(
                "¿Deseas que Script-Tools intente instalar FFmpeg automáticamente con winget ahora?", default=True
            ):
                console.print("\n[cyan]Ejecutando: winget install -e --id Gyan.FFmpeg...[/cyan]")
                subprocess.run(["winget", "install", "-e", "--id", "Gyan.FFmpeg"])
                console.print(
                    "[yellow]Nota: Si la instalación terminó, reinicia tu terminal para que tome efecto en el PATH.[/yellow]"
                )
        elif sys.platform == "darwin" and shutil.which("brew"):
            if Confirm.ask("¿Deseas que Script-Tools intente instalar FFmpeg con Homebrew ahora?", default=True):
                console.print("\n[cyan]Ejecutando: brew install ffmpeg...[/cyan]")
                subprocess.run(["brew", "install", "ffmpeg"])
        Prompt.ask("\n[dim]Presiona Enter para continuar...[/dim]")
        return

    console.print("[bold]¿Cómo deseas seleccionar el video?[/bold]")
    console.print("  [1] 📂 Abrir ventana de selección de archivos (Recomendado)")
    console.print("  [2] ✍️  Escribir o arrastrar la ruta del video aquí")
    console.print("  [0] ↩️  Volver al menú principal")

    mode = Prompt.ask("Opción", choices=["1", "2", "0"], default="1")
    if mode == "0":
        return

    video_path = None
    if mode == "1":
        import compress_video

        video_path = compress_video.interactive_gui_picker()
        if not video_path:
            console.print("[yellow]Selección cancelada.[/yellow]")
            return
    else:
        raw_path = Prompt.ask("Ruta del archivo de video").strip().strip('"').strip("'")
        video_path = Path(raw_path)
        if not video_path.exists():
            console.print(f"[bold red]El archivo no existe: {video_path}[/bold red]")
            Prompt.ask("[dim]Presiona Enter para continuar...[/dim]")
            return

    console.print(f"\n[green]Archivo seleccionado:[/green] [bold]{video_path.name}[/bold]")
    console.print("[bold]Selecciona el perfil de compresión:[/bold]")
    console.print("  [1] 💬 WhatsApp / Correo (< 15 MB exacto, cálculo de 2 pasadas)")
    console.print("  [2] 🎮 Discord Free (< 25 MB, compatibilidad universal H.264)")
    console.print("  [3] ⚖️  Alta Fidelidad Equilibrada (1080p, H.265 / HEVC) [Recomendado]")
    console.print("  [4] 🚀 Máxima Eficiencia AV1 (Nuevo códec, máxima reducción)")
    console.print("  [5] ⚡ Ultra Rápido por Hardware GPU (NVENC / QSV / AMF)")
    console.print("  [0] ↩️  Volver")

    preset_choice = Prompt.ask("Perfil", choices=["1", "2", "3", "4", "5", "0"], default="3")
    if preset_choice == "0":
        return

    extra_args = [str(video_path)]
    if preset_choice == "1":
        extra_args += ["--target-size", "15MB"]
    elif preset_choice == "2":
        extra_args += ["--target-size", "25MB", "--codec", "h264"]
    elif preset_choice == "3":
        extra_args += ["--codec", "hevc", "--preset", "balanced"]
    elif preset_choice == "4":
        extra_args += ["--codec", "av1", "--preset", "high"]
    elif preset_choice == "5":
        extra_args += ["--hwaccel", "auto", "--preset", "draft"]

    console.print(f"\n[cyan]Iniciando compresión de [bold]{video_path.name}[/bold]...[/cyan]\n")
    dispatch_video(extra_args)
    Prompt.ask("\n[bold green]Presiona Enter para volver al menú...[/bold green]")


def _interactive_pdf():
    console.print()
    console.print(
        Panel(
            "[bold cyan]📄  Optimizador de Documentos PDF (OCR-Safe)[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED,
        )
    )

    console.print("[bold]¿Cómo deseas seleccionar el documento PDF?[/bold]")
    console.print("  [1] 📂 Abrir ventana de selección de archivos (Recomendado)")
    console.print("  [2] ✍️  Escribir o arrastrar la ruta del PDF aquí")
    console.print("  [0] ↩️  Volver al menú principal")

    mode = Prompt.ask("Opción", choices=["1", "2", "0"], default="1")
    if mode == "0":
        return

    pdf_path = None
    if mode == "1":
        import pdf_optimizer

        pdf_path = pdf_optimizer.interactive_gui_picker()
        if not pdf_path:
            console.print("[yellow]Selección cancelada.[/yellow]")
            return
    else:
        raw_path = Prompt.ask("Ruta del documento PDF").strip().strip('"').strip("'")
        pdf_path = Path(raw_path)
        if not pdf_path.exists():
            console.print(f"[bold red]El archivo no existe: {pdf_path}[/bold red]")
            Prompt.ask("[dim]Presiona Enter para continuar...[/dim]")
            return

    console.print(f"\n[green]Archivo seleccionado:[/green] [bold]{pdf_path.name}[/bold]")
    console.print("[bold]Selecciona el perfil de optimización:[/bold]")
    console.print("  [1] ⚖️  Equilibrado (150 DPI - Tareas universitarias, correo, lectura) [Recomendado]")
    console.print("  [2] 📱 Pantalla / Aula Virtual (72 DPI - Cuotas estrictas < 5 MB)")
    console.print("  [3] 🖨️  Impresión Formal (300 DPI - Portafolios y documentos oficiales)")
    console.print("  [4] 💎 Sin Pérdida (0% degradación visual, reorganización de objetos)")
    console.print("  [0] ↩️  Volver")

    profile_choice = Prompt.ask("Perfil", choices=["1", "2", "3", "4", "0"], default="1")
    if profile_choice == "0":
        return

    profiles = {
        "1": "balanced",
        "2": "screen",
        "3": "print",
        "4": "lossless",
    }
    selected_profile = profiles[profile_choice]

    strict_ocr = Confirm.ask("¿Deseas verificar y proteger estrictamente la capa de texto OCR?", default=True)

    extra_args = [str(pdf_path), "--profile", selected_profile]
    if strict_ocr:
        extra_args.append("--strict-ocr")

    console.print(
        f"\n[cyan]Iniciando optimización de [bold]{pdf_path.name}[/bold] con perfil '{selected_profile}'...[/cyan]\n"
    )
    dispatch_pdf(extra_args)
    Prompt.ask("\n[bold green]Presiona Enter para volver al menú...[/bold green]")


def _interactive_doctor():
    console.print()
    console.print(
        Panel(
            "[bold cyan]🩺  Auditoría del Entorno de Desarrollo (Dev Doctor)[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED,
        )
    )
    dispatch_doctor([])
    Prompt.ask("\n[bold green]Presiona Enter para volver al menú...[/bold green]")


def _interactive_backup():
    console.print()
    platform_title = "Windows" if sys.platform == "win32" else ("macOS" if sys.platform == "darwin" else "Linux")
    console.print(
        Panel(
            f"[bold cyan]💾  Respaldo Exhaustivo Pre-Formateo ({platform_title})[/bold cyan]\n"
            "[dim]Genera un snapshot del entorno dev y script automatizado de restauración[/dim]",
            border_style="cyan",
            box=box.ROUNDED,
        )
    )

    console.print("Se creará una carpeta con el inventario completo de:")
    if sys.platform == "win32":
        console.print("  • Paquetes Winget, aplicaciones Scoop y Chocolatey")
        console.print("  • Extensiones, settings.json y snippets de VS Code")
        console.print("  • Compiladores (MSVC, GCC, Clang, CMake, Ninja)")
        console.print("  • Runtimes (Python, Node.js, .NET, Rust/Cargo)")
        console.print("  • Variables de entorno del sistema y de usuario (.reg)")
        console.print("  • Asistente interactivo de restauración [bold]REINSTALL.ps1[/bold]\n")
    elif sys.platform == "darwin":
        console.print("  • Homebrew Brewfile (fórmulas, casks y dependencias instaladas)")
        console.print("  • Extensiones, settings.json y snippets de VS Code")
        console.print("  • Configuración global de Git (.gitconfig)")
        console.print("  • Perfiles de shell (~/.zshrc, ~/.bash_profile)")
        console.print("  • Llaves públicas SSH y known_hosts")
        console.print("  • Script de auto-restauración [bold]restore.sh[/bold]\n")
    else:
        console.print("  • Paquetes del sistema (APT, Pacman o DNF) y aplicaciones Flatpak")
        console.print("  • Extensiones, settings.json y snippets de VS Code")
        console.print("  • Configuración global de Git (.gitconfig)")
        console.print("  • Perfiles de shell (~/.bashrc, ~/.zshrc)")
        console.print("  • Llaves públicas SSH y known_hosts")
        console.print("  • Script de auto-restauración [bold]restore.sh[/bold]\n")

    if Confirm.ask("¿Deseas iniciar el respaldo ahora?", default=True):
        dispatch_backup([])
    Prompt.ask("\n[bold green]Presiona Enter para volver al menú...[/bold green]")


def _interactive_context_menu():
    console.print()
    console.print(
        Panel(
            "[bold cyan]🖱️  Integración al Menú Contextual / Sistema[/bold cyan]\n"
            "[dim]Permite acceder rápidamente a la compresión y optimización multimedia[/dim]",
            border_style="cyan",
            box=box.ROUNDED,
        )
    )

    if sys.platform == "win32":
        console.print("[bold]Selecciona una acción para Windows Explorer:[/bold]")
        console.print("  [1] 📥 Instalar accesos directos (Clic derecho > Comprimir / Optimizar)")
        console.print("  [2] 📤 Desinstalar accesos directos de Script-Tools")
        console.print("  [0] ↩️  Volver")

        choice = Prompt.ask("Opción", choices=["1", "2", "0"], default="1")
        if choice == "1":
            script = ROOT_DIR / "scripts" / "install_context_menu.ps1"
            subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)])
        elif choice == "2":
            script = ROOT_DIR / "scripts" / "uninstall_context_menu.ps1"
            subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)])
    else:
        console.print("[green]En Linux y macOS, Script-Tools se integra mediante comando global de terminal:[/green]\n")
        console.print("  1. Ejecutable directo local: [bold cyan]./tools.sh[/bold cyan]")
        console.print("  2. Instalación como comando de sistema: [bold cyan]pip install -e .[/bold cyan]")
        console.print("     Luego podrás escribir directamente [bold]tools menu[/bold] o [bold]tools video ...[/bold]")
        console.print('  3. Autocompletado de shell: [bold cyan]eval "$(tools completion bash)"[/bold cyan] o zsh\n')
    Prompt.ask("\n[bold green]Presiona Enter para volver al menú...[/bold green]")


def run_interactive_menu() -> int:
    """Renders the master interactive terminal dashboard and dispatches actions."""
    while True:
        console.print()
        banner = (
            "[bold cyan]🛠️  SCRIPT-TOOLS DEVELOPER SUITE[/bold cyan]\n"
            "[dim]Automatización, Optimización Multimedia y Diagnóstico de Sistemas[/dim]"
        )
        console.print(Panel(banner, border_style="cyan", box=box.ROUNDED))

        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2), expand=False)
        table.add_column("Opción", style="bold green", width=6)
        table.add_column("Herramienta", style="bold white", width=26)
        table.add_column("Capacidades Clave", style="dim")

        table.add_row("[1]", "🎥 Comprimir Video", "AV1, HEVC, WhatsApp (15MB), Discord, Aceleración GPU")
        table.add_row("[2]", "📄 Optimizar PDF", "150/72 DPI, preservación 100% OCR, ahorro hasta 85%")
        table.add_row("[3]", "🩺 Auditoría Dev Doctor", "Salud de VS Code, Git, Compiladores (C/C++), Runtimes, PATH")
        table.add_row(
            "[4]",
            "💾 Respaldo Pre-Formateo",
            "Snapshot dev (Windows Winget/Scoop, macOS Homebrew, Linux APT/Pacman)",
        )
        table.add_row(
            "[5]",
            "🖱️ Integración Sistema",
            "Menú contextual Explorer (Windows) / Comando global CLI (macOS/Linux)",
        )
        table.add_row("[0]", "🚪 Salir", "Cerrar la suite")

        console.print(table)
        console.print()

        choice = Prompt.ask(
            "[bold yellow]Selecciona una opción[/bold yellow]",
            choices=["1", "2", "3", "4", "5", "0"],
            default="1",
        )

        if choice == "0":
            console.print("\n[green]¡Hasta pronto![/green]\n")
            return 0
        elif choice == "1":
            _interactive_video()
        elif choice == "2":
            _interactive_pdf()
        elif choice == "3":
            _interactive_doctor()
        elif choice == "4":
            _interactive_backup()
        elif choice == "5":
            _interactive_context_menu()


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="tools",
        description="🛠️ Script-Tools: Windows Automation & Multiplatform Developer Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Comandos disponibles:
  tools menu        Menú interactivo visual TUI con navegación guiada
  tools video       Compresor de video acelerado por GPU (AV1, H.265, H.264, 2-Pass Target Size)
  tools pdf         Optimizador de PDFs con preservación estricta de OCR y motor híbrido
  tools doctor      Auditoría de salud del entorno de desarrollo (VS Code, Git, C/C++, Runtimes)
  tools backup      Snapshot integral pre-formateo para Windows (Winget, Scoop, VS Code, Git)
  tools completion  Generador de auto-completado de terminal (powershell, bash, zsh)

Ejemplos:
  tools.bat                         (Doble clic o launcher directo en Windows)
  python tools.py menu              (Menú interactivo visual guiado)
  python tools.py video clase.mp4 --target-size 15MB
  python tools.py pdf reporte.pdf --profile balanced
  python tools.py doctor
  python tools.py backup
  python tools.py completion powershell
        """,
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 2.0.0")
    parser.add_argument("-i", "--interactive", action="store_true", help="Lanza el menú interactivo visual TUI")

    subparsers = parser.add_subparsers(dest="command", help="Herramienta a ejecutar")

    # menu
    subparsers.add_parser(
        "menu",
        help="Abre el menú interactivo visual en la terminal",
        add_help=False,
    )
    # video
    subparsers.add_parser(
        "video",
        help="Comprime videos con aceleracion por hardware y soporte multi-codec",
        add_help=False,
    )
    # pdf
    subparsers.add_parser(
        "pdf",
        help="Optimiza documentos PDF preservando OCR",
        add_help=False,
    )
    # doctor
    subparsers.add_parser(
        "doctor",
        help="Diagnostica la salud de VS Code y el toolchain de desarrollo",
        add_help=False,
    )
    # backup
    subparsers.add_parser(
        "backup",
        help="Ejecuta el respaldo exhaustivo previo a formatear (Windows)",
        add_help=False,
    )
    # completion
    subparsers.add_parser(
        "completion",
        help="Genera scripts de autocompletado para terminales (powershell, bash, zsh)",
        add_help=False,
    )

    if len(sys.argv) < 2:
        parser.print_help()
        return 0

    parsed_args, extra_args = parser.parse_known_args()

    if parsed_args.interactive or parsed_args.command == "menu":
        if "-h" in extra_args or "--help" in extra_args:
            print(
                "Uso: tools menu [-h]\n\nAbre la interfaz interactiva visual (TUI) para acceder a todas las herramientas."
            )
            return 0
        return run_interactive_menu()

    command = parsed_args.command
    if not command:
        first_arg = extra_args[0] if extra_args else "desconocido"
        sys.stderr.write(f"[ERROR] Subcomando no reconocido: '{first_arg}'\n\n")
        parser.print_help(sys.stderr)
        return 2

    if command == "video":
        return dispatch_video(extra_args)
    elif command == "pdf":
        return dispatch_pdf(extra_args)
    elif command == "doctor":
        return dispatch_doctor(extra_args)
    elif command == "backup":
        return dispatch_backup(extra_args)
    elif command == "completion":
        return dispatch_completion(extra_args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.stderr.write("\n[AVISO] Operación cancelada por el usuario.\n")
        sys.exit(130)
