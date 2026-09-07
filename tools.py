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

# Enable UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

ROOT_DIR = Path(__file__).resolve().parent

# Ensure sub-packages are discoverable
for subdir in ["video-compressor", "pdf-optimizer", "vscode-path-doctor"]:
    path_str = str(ROOT_DIR / subdir)
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
    """Dispatches system pre-format backup on Windows."""
    if sys.platform != "win32":
        sys.stderr.write("[ERROR] System Pre-Format Backup is designed specifically for Windows.\n")
        return 1
    script = ROOT_DIR / "system-backup-preformat" / "backup_preformat.ps1"
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)] + extra_args
    try:
        return subprocess.run(cmd).returncode
    except FileNotFoundError:
        sys.stderr.write("[ERROR] 'powershell' no está disponible en el PATH del sistema.\n")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="tools",
        description="🛠️ Script-Tools: Windows Automation & Multiplatform Developer Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Comandos disponibles:
  tools video       Compresor de video acelerado por GPU (AV1, H.265, H.264, 2-Pass Target Size)
  tools pdf         Optimizador de PDFs con preservacion estricta de OCR y motor hibrido
  tools doctor      Auditoria de salud del entorno de desarrollo (VS Code, Git, C/C++, Runtimes)
  tools backup      Snapshot integral pre-formateo para Windows (Winget, Scoop, VS Code, Git)
  tools completion  Generador de auto-completado de terminal (powershell, bash, zsh)

Ejemplos:
  python tools.py video clase.mp4 --target-size 15MB
  python tools.py pdf reporte.pdf --profile balanced
  python tools.py doctor
  python tools.py backup
  python tools.py completion powershell
        """,
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 2.0.0")

    subparsers = parser.add_subparsers(dest="command", help="Herramienta a ejecutar")

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
