#!/usr/bin/env python3
"""
Video Compressor - Multiplatform, Hardware-Accelerated Video Compression Tool.
Supports AV1, HEVC (H.265), AVC (H.264), and VP9 with automatic GPU detection,
CRF quality presets, and two-pass target-size compression.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
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

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".m4v", ".wmv", ".ts"}

CODEC_MAP = {
    "hevc": {
        "cpu": "libx265",
        "nvenc": "hevc_nvenc",
        "videotoolbox": "hevc_videotoolbox",
        "qsv": "hevc_qsv",
        "amf": "hevc_amf",
        "default_crf": 28,
    },
    "h264": {
        "cpu": "libx264",
        "nvenc": "h264_nvenc",
        "videotoolbox": "h264_videotoolbox",
        "qsv": "h264_qsv",
        "amf": "h264_amf",
        "default_crf": 23,
    },
    "av1": {
        "cpu": "libsvtav1",
        "nvenc": "av1_nvenc",
        "qsv": "av1_qsv",
        "amf": "av1_amf",
        "default_crf": 32,
    },
    "vp9": {
        "cpu": "libvpx-vp9",
        "qsv": "vp9_qsv",
        "default_crf": 34,
    },
}

PRESET_CRF_OFFSETS = {
    "archival": -4,
    "high": -2,
    "balanced": 0,
    "draft": 6,
}


@dataclass
class VideoMetadata:
    duration_sec: float
    width: int
    height: int
    bitrate_kbps: float
    video_codec: str
    audio_codec: Optional[str]
    size_bytes: int


def get_ffmpeg_binary() -> str:
    """Returns path to ffmpeg or exits with helpful instructions."""
    binary = shutil.which("ffmpeg")
    if not binary:
        try:
            from rich import box
            from rich.console import Console
            from rich.panel import Panel

            c = Console()
            c.print()
            c.print(
                Panel(
                    "[bold red]FFmpeg no está instalado o no se encuentra en el PATH del sistema.[/bold red]\n\n"
                    "El compresor requiere FFmpeg para la codificación y decodificación de video.\n\n"
                    "Comando para instalar en Windows (PowerShell / CMD):\n"
                    "  [bold cyan]winget install Gyan.FFmpeg[/bold cyan]\n"
                    "  o con Scoop:\n"
                    "  [bold cyan]scoop install ffmpeg[/bold cyan]\n\n"
                    "En macOS: [bold cyan]brew install ffmpeg[/bold cyan] | En Linux: [bold cyan]sudo apt install ffmpeg[/bold cyan]",
                    title="[bold yellow]Dependencia Requerida: FFmpeg[/bold yellow]",
                    border_style="red",
                    box=box.ROUNDED,
                )
            )
        except Exception:
            sys.stderr.write(
                "\n[ERROR] FFmpeg is not installed or not found in system PATH.\n"
                "Please install FFmpeg to continue:\n"
                "  - Windows: scoop install ffmpeg  OR  winget install Gyan.FFmpeg\n"
                "  - macOS:   brew install ffmpeg\n"
                "  - Linux:   sudo apt install ffmpeg\n\n"
            )
        if sys.stdin.isatty():
            try:
                input("\nPresiona Enter para continuar...")
            except Exception:
                pass
        sys.exit(1)
    return binary


def get_ffprobe_binary() -> str:
    """Returns path to ffprobe or falls back to ffmpeg search."""
    binary = shutil.which("ffprobe")
    if not binary:
        ffmpeg = get_ffmpeg_binary()
        sibling = Path(ffmpeg).parent / ("ffprobe.exe" if sys.platform == "win32" else "ffprobe")
        if sibling.exists():
            return str(sibling)
        sys.stderr.write("[ERROR] ffprobe is required for media inspection.\n")
        sys.exit(1)
    return binary


def detect_available_encoders(ffmpeg_bin: str) -> set[str]:
    """Inspects FFmpeg binary to find compiled and available encoders."""
    try:
        proc = subprocess.run(
            [ffmpeg_bin, "-encoders"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        encoders = set()
        for line in proc.stdout.splitlines():
            parts = line.strip().split()
            if len(parts) >= 2 and parts[0].startswith("V"):
                encoders.add(parts[1])
        return encoders
    except Exception:
        return set()


def probe_video(file_path: Path) -> Optional[VideoMetadata]:
    """Extracts duration, resolution, codecs, and stream properties."""
    ffprobe = get_ffprobe_binary()
    cmd = [
        ffprobe,
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(file_path),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(proc.stdout)

        format_info = data.get("format", {})
        duration = float(format_info.get("duration", 0.0))
        size_bytes = int(format_info.get("size", file_path.stat().st_size))
        total_bitrate = float(format_info.get("bit_rate", 0.0)) / 1000.0

        v_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
        a_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)

        if not v_stream:
            return None

        width = int(v_stream.get("width", 0))
        height = int(v_stream.get("height", 0))
        v_codec = v_stream.get("codec_name", "unknown")
        a_codec = a_stream.get("codec_name") if a_stream else None

        if duration == 0.0 and "duration" in v_stream:
            duration = float(v_stream["duration"])

        return VideoMetadata(
            duration_sec=duration,
            width=width,
            height=height,
            bitrate_kbps=total_bitrate,
            video_codec=v_codec,
            audio_codec=a_codec,
            size_bytes=size_bytes,
        )
    except Exception as err:
        sys.stderr.write(f"[WARN] Could not probe {file_path.name}: {err}\n")
        return None


def select_best_encoder(
    target_codec: str,
    hw_pref: str,
    available_encoders: set[str],
) -> Tuple[str, str]:
    """
    Selects the optimal FFmpeg encoder name based on requested codec and hardware acceleration.
    Returns: (encoder_name, acceleration_type)
    """
    codec_info = CODEC_MAP.get(target_codec, CODEC_MAP["hevc"])

    if hw_pref == "cpu":
        return codec_info["cpu"], "cpu"

    # Hardware priority list
    hw_candidates = [
        ("nvenc", "NVIDIA NVENC"),
        ("videotoolbox", "Apple VideoToolbox"),
        ("qsv", "Intel QuickSync"),
        ("amf", "AMD AMF"),
    ]

    if hw_pref != "auto":
        enc_name = codec_info.get(hw_pref)
        if enc_name and enc_name in available_encoders:
            return enc_name, hw_pref
        sys.stderr.write(f"[WARN] Requested hardware '{hw_pref}' unavailable. Falling back to auto.\n")

    for hw_key, label in hw_candidates:
        enc_name = codec_info.get(hw_key)
        if enc_name and enc_name in available_encoders:
            return enc_name, label

    return codec_info["cpu"], "CPU (Software)"


def parse_size_to_bytes(size_str: str) -> Optional[int]:
    """Parses size strings like '10MB', '25M', '500KB', '1.5GB' into bytes."""
    clean = size_str.strip().upper()
    units = {
        "KB": 1024,
        "K": 1024,
        "MB": 1024 * 1024,
        "M": 1024 * 1024,
        "GB": 1024 * 1024 * 1024,
        "G": 1024 * 1024 * 1024,
    }
    parsed_bytes: Optional[int] = None
    for unit, multiplier in sorted(units.items(), key=lambda x: -len(x[0])):
        if clean.endswith(unit):
            num_part = clean[: -len(unit)].strip()
            try:
                parsed_bytes = int(float(num_part) * multiplier)
                break
            except ValueError:
                return None
    if parsed_bytes is None:
        try:
            parsed_bytes = int(float(clean) * 1024 * 1024)
        except ValueError:
            return None

    return parsed_bytes if parsed_bytes > 0 else None


def format_bytes(size: float) -> str:
    """Formats bytes to readable MB/GB string."""
    if size >= 1024 * 1024 * 1024:
        return f"{size / (1024**3):.2f} GB"
    return f"{size / (1024**2):.2f} MB"


def build_scale_filter(resolution_str: str, meta: VideoMetadata) -> Optional[str]:
    """Builds an aspect-ratio-safe scale filter ensuring even dimensions."""
    if resolution_str == "keep" or resolution_str == "original":
        return "scale=trunc(iw/2)*2:trunc(ih/2)*2"

    try:
        target_h = int(resolution_str.replace("p", ""))
    except ValueError:
        return "scale=trunc(iw/2)*2:trunc(ih/2)*2"

    if meta.height > 0 and meta.height <= target_h:
        return "scale=trunc(iw/2)*2:trunc(ih/2)*2"

    return f"scale=-2:{target_h}"


def run_ffmpeg_with_progress(cmd: List[str], duration_sec: float, desc: str = "Procesando video") -> bool:
    """Executes FFmpeg with real-time percentage progress bar parsed from -progress pipe:1."""
    full_cmd = cmd[:-1] + ["-progress", "pipe:1", "-nostats"] + [cmd[-1]]
    proc: Optional[subprocess.Popen[str]] = None
    try:
        from rich.console import Console
        from rich.progress import (
            BarColumn,
            Progress,
            SpinnerColumn,
            TaskProgressColumn,
            TextColumn,
            TimeRemainingColumn,
        )

        console = Console()
        proc = subprocess.Popen(
            full_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]{task.description}"),
            BarColumn(bar_width=30),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task(desc, total=100.0)
            if proc.stdout:
                for line in proc.stdout:
                    if "out_time_us=" in line or "out_time_ms=" in line:
                        try:
                            val = int(line.strip().split("=")[1])
                            curr_sec = val / 1_000_000.0
                            if duration_sec > 0:
                                pct = min(100.0, max(0.0, (curr_sec / duration_sec) * 100.0))
                                progress.update(task, completed=pct)
                        except (ValueError, IndexError):
                            pass
                    elif "progress=end" in line:
                        progress.update(task, completed=100.0)

        proc.wait()
        return proc.returncode == 0
    except KeyboardInterrupt:
        if proc:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
        raise
    except Exception:
        if proc:
            proc.kill()
        return subprocess.run(cmd).returncode == 0


def compress_video(
    input_file: Path,
    output_file: Path,
    codec: str = "hevc",
    preset: str = "balanced",
    resolution: str = "keep",
    target_size_str: Optional[str] = None,
    hwaccel: str = "auto",
    crf_override: Optional[int] = None,
    audio_mode: str = "aac",
    audio_bitrate: str = "64k",
    speed_preset: str = "medium",
) -> bool:
    """Executes FFmpeg compression pipeline with either CRF or Two-Pass Bitrate mode."""
    ffmpeg = get_ffmpeg_binary()
    available_encoders = detect_available_encoders(ffmpeg)
    meta = probe_video(input_file)

    if not meta:
        sys.stderr.write(f"[ERROR] Could not extract metadata from {input_file.name}\n")
        return False

    encoder_name, hw_label = select_best_encoder(codec, hwaccel, available_encoders)
    scale_filter = build_scale_filter(resolution, meta)

    output_file.parent.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 64)
    print(f" 🎬 Video: {input_file.name}")
    print(
        f" 📊 Input: {format_bytes(meta.size_bytes)} | Duration: {meta.duration_sec:.1f}s | Resolution: {meta.width}x{meta.height}"
    )
    print(f" ⚙️  Encoder: {encoder_name} ({hw_label}) | Codec: {codec.upper()}")
    print("=" * 64)

    audio_args: List[str] = []
    if audio_mode == "mute" or meta.audio_codec is None:
        audio_args = ["-an"]
    elif audio_mode == "copy":
        audio_args = ["-c:a", "copy"]
    elif audio_mode == "opus":
        audio_args = ["-c:a", "libopus", "-b:a", audio_bitrate]
    else:  # aac
        audio_args = ["-c:a", "aac", "-b:a", audio_bitrate]

    start_time = time.time()

    target_bytes = parse_size_to_bytes(target_size_str) if target_size_str else None
    if target_bytes:
        if meta.duration_sec <= 0:
            sys.stderr.write("[ERROR] Video duration is 0, cannot calculate target bitrate.\n")
            return False

        audio_bps = 64_000 if audio_mode != "mute" else 0
        total_target_bits = target_bytes * 8 * 0.95
        total_bitrate_bps = total_target_bits / meta.duration_sec
        video_bitrate_bps = max(total_bitrate_bps - audio_bps, 100_000)
        video_kbps = int(video_bitrate_bps / 1000)

        print(f" 🧮 Two-Pass Mode: Aiming for {format_bytes(target_bytes)} (Target video bitrate: {video_kbps} kbps)")

        temp_pass_dir = tempfile.mkdtemp(prefix="ffpass_")
        pass_log_prefix = str(Path(temp_pass_dir) / "passlog")
        null_out = "NUL" if sys.platform == "win32" else "/dev/null"
        pass1_cmd = [
            ffmpeg,
            "-y",
            "-i",
            str(input_file),
            "-c:v",
            encoder_name,
            "-b:v",
            f"{video_kbps}k",
            "-pass",
            "1",
            "-passlogfile",
            pass_log_prefix,
            "-an",
            "-f",
            "null",
        ]
        if scale_filter:
            pass1_cmd.extend(["-vf", scale_filter])
        pass1_cmd.append(null_out)

        pass2_cmd = [
            ffmpeg,
            "-y",
            "-i",
            str(input_file),
            "-c:v",
            encoder_name,
            "-b:v",
            f"{video_kbps}k",
            "-pass",
            "2",
            "-passlogfile",
            pass_log_prefix,
        ]
        pass2_cmd.extend(audio_args)
        if scale_filter:
            pass2_cmd.extend(["-vf", scale_filter])
        pass2_cmd.extend(["-movflags", "+faststart", str(output_file)])

        try:
            ok1 = run_ffmpeg_with_progress(pass1_cmd, meta.duration_sec, desc="Paso 1/2: Analizando video")
            if not ok1:
                if output_file.exists():
                    output_file.unlink(missing_ok=True)
                return False
            ok2 = run_ffmpeg_with_progress(pass2_cmd, meta.duration_sec, desc="Paso 2/2: Comprimiendo video")
            if not ok2:
                if output_file.exists():
                    output_file.unlink(missing_ok=True)
                return False
        except Exception as err:
            if output_file.exists():
                output_file.unlink(missing_ok=True)
            sys.stderr.write(f"\n[ERROR] FFmpeg failed during two-pass encoding: {err}\n")
            return False
        finally:
            shutil.rmtree(temp_pass_dir, ignore_errors=True)

    else:
        base_crf = CODEC_MAP.get(codec, CODEC_MAP["hevc"])["default_crf"]
        offset = PRESET_CRF_OFFSETS.get(preset, 0)
        final_crf = crf_override if crf_override is not None else (base_crf + offset)

        cmd = [
            ffmpeg,
            "-y",
            "-i",
            str(input_file),
            "-c:v",
            encoder_name,
        ]

        if "nvenc" in encoder_name:
            cmd.extend(["-cq", str(final_crf), "-preset", "p5"])
        elif "videotoolbox" in encoder_name:
            cmd.extend(["-q:v", str(final_crf)])
        elif "qsv" in encoder_name:
            cmd.extend(["-global_quality", str(final_crf)])
        elif encoder_name == "libsvtav1":
            cmd.extend(["-crf", str(final_crf), "-preset", "6"])
        elif encoder_name == "libvpx-vp9":
            cmd.extend(["-crf", str(final_crf), "-b:v", "0"])
        else:  # libx264 / libx265
            cmd.extend(["-crf", str(final_crf), "-preset", speed_preset])

        if scale_filter:
            cmd.extend(["-vf", scale_filter])

        cmd.extend(audio_args)
        cmd.extend(["-movflags", "+faststart", str(output_file)])

        print(f" ⚙️  Mode: CRF {final_crf} (Preset: {preset}) | Speed: {speed_preset}")
        ok = run_ffmpeg_with_progress(cmd, meta.duration_sec, desc="Comprimiendo video")
        if not ok:
            if output_file.exists():
                output_file.unlink(missing_ok=True)
            sys.stderr.write("\n[ERROR] FFmpeg failed during compression\n")
            return False

    elapsed = time.time() - start_time
    if output_file.exists() and output_file.stat().st_size > 0:
        out_size = output_file.stat().st_size
        saved_bytes = meta.size_bytes - out_size
        ratio = (saved_bytes / meta.size_bytes) * 100.0 if meta.size_bytes > 0 else 0

        print("\n" + "─" * 64)
        print(f" ✅ Compression Finished in {elapsed:.1f} seconds!")
        print(f" 📦 Output:    {format_bytes(out_size)} ({ratio:+.1f}% space saved)")
        print(f" 📁 Saved to:  {output_file.resolve()}")
        print("─" * 64 + "\n")
        return True
    else:
        if output_file.exists():
            output_file.unlink(missing_ok=True)
        sys.stderr.write("[ERROR] Output file was not created or is empty.\n")
        return False


def interactive_gui_picker() -> Optional[Path]:
    """Displays a native file picker dialog if GUI is available."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        file_selected = filedialog.askopenfilename(
            title="Seleccionar Video para Comprimir",
            filetypes=[("Videos", "*.mp4 *.mkv *.mov *.avi *.webm *.flv *.m4v *.wmv"), ("Todos los archivos", "*.*")],
        )
        root.destroy()
        return Path(file_selected) if file_selected else None
    except Exception:
        return None


def interactive_workflow() -> int:
    """Guided interactive workflow with Rich UI when no arguments are provided."""
    try:
        from rich import box
        from rich.console import Console
        from rich.panel import Panel
        from rich.prompt import Confirm, Prompt

        c = Console()
        c.print()
        c.print(
            Panel(
                "[bold cyan]🎥  COMPRESOR DE VIDEO - SCRIPT-TOOLS[/bold cyan]\n"
                "[dim]Aceleración por GPU, Multi-Códec (AV1/HEVC/H264) y Modo Target 2-Pass[/dim]",
                box=box.ROUNDED,
                border_style="cyan",
            )
        )

        if not shutil.which("ffmpeg"):
            c.print(
                Panel(
                    "[bold red]FFmpeg no está instalado en el sistema.[/bold red]\n\n"
                    "Para comprimir videos se requiere FFmpeg en el PATH.\n"
                    "Puedes instalarlo en Windows ejecutando:\n"
                    "  [bold cyan]winget install Gyan.FFmpeg[/bold cyan]\n"
                    "  o con Scoop: [bold cyan]scoop install ffmpeg[/bold cyan]",
                    title="[bold yellow]Dependencia Requerida[/bold yellow]",
                    border_style="red",
                    box=box.ROUNDED,
                )
            )
            if sys.platform == "win32" and shutil.which("winget"):
                if Confirm.ask("¿Deseas que Script-Tools intente instalar FFmpeg con winget ahora?", default=True):
                    subprocess.run(["winget", "install", "-e", "--id", "Gyan.FFmpeg"])
                    c.print("[yellow]Si la instalación terminó, reinicia tu consola para actualizar el PATH.[/yellow]")
            Prompt.ask("\n[dim]Presiona Enter para salir...[/dim]")
            return 1

        c.print("[bold]¿Cómo deseas seleccionar el video?[/bold]")
        c.print("  [1] 📂 Abrir ventana de selección de archivos (Recomendado)")
        c.print("  [2] ✍️  Escribir o arrastrar la ruta del video aquí")
        c.print("  [0] 🚪 Cancelar")
        pick_mode = Prompt.ask("Opción", choices=["1", "2", "0"], default="1")
        if pick_mode == "0":
            return 0

        video_file = None
        if pick_mode == "1":
            video_file = interactive_gui_picker()
            if not video_file:
                c.print("[yellow]Selección cancelada.[/yellow]")
                return 0
        else:
            raw = Prompt.ask("Ruta del archivo de video").strip().strip('"').strip("'")
            video_file = Path(raw)
            if not video_file.exists():
                c.print(f"[bold red]El archivo no existe: {video_file}[/bold red]")
                Prompt.ask("\n[dim]Presiona Enter para salir...[/dim]")
                return 1

        c.print(f"\n[green]Archivo seleccionado:[/green] [bold]{video_file.name}[/bold]")
        c.print("[bold]Selecciona el perfil de compresión:[/bold]")
        c.print("  [1] 💬 WhatsApp / Correo (< 15 MB exacto, cálculo de 2 pasadas)")
        c.print("  [2] 🎮 Discord Free (< 25 MB, formato universal H.264)")
        c.print("  [3] ⚖️  Alta Fidelidad Equilibrada (1080p, H.265 / HEVC) [Recomendado]")
        c.print("  [4] 🚀 Máxima Eficiencia AV1 (Nuevo códec, máxima reducción)")
        c.print("  [5] ⚡ Rápido por Hardware GPU (NVENC / QSV / AMF)")
        c.print("  [0] 🚪 Cancelar")

        preset_choice = Prompt.ask("Perfil", choices=["1", "2", "3", "4", "5", "0"], default="3")
        if preset_choice == "0":
            return 0

        codec = "hevc"
        preset = "balanced"
        target_size = None
        hwaccel = "auto"
        resolution = "keep"

        if preset_choice == "1":
            target_size = "15MB"
        elif preset_choice == "2":
            target_size = "25MB"
            codec = "h264"
        elif preset_choice == "3":
            codec = "hevc"
            preset = "balanced"
        elif preset_choice == "4":
            codec = "av1"
            preset = "high"
        elif preset_choice == "5":
            hwaccel = "auto"
            preset = "draft"

        out_file = video_file.parent / f"{video_file.stem}_compressed.mp4"
        c.print(f"\n[cyan]Iniciando compresión de [bold]{video_file.name}[/bold]...[/cyan]\n")
        ok = compress_video(
            input_file=video_file,
            output_file=out_file,
            codec=codec,
            preset=preset,
            resolution=resolution,
            target_size_str=target_size,
            hwaccel=hwaccel,
        )
        if ok:
            c.print(f"\n[bold green]✓ Video comprimido exitosamente: {out_file}[/bold green]")
        else:
            c.print("\n[bold red]✗ No se pudo completar la compresión del video.[/bold red]")

        Prompt.ask("\n[bold green]Presiona Enter para salir...[/bold green]")
        return 0 if ok else 1
    except Exception as e:
        sys.stderr.write(f"[ERROR] {e}\n")
        if sys.stdin.isatty():
            try:
                input("\nPresiona Enter para salir...")
            except Exception:
                pass
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Video Compressor - Multiplatform, Hardware-Accelerated Video Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python compress_video.py video.mp4
  python compress_video.py video.mkv --codec av1 --preset high
  python compress_video.py video.mp4 --target-size 15MB
  python compress_video.py video.mp4 --resolution 720p --codec hevc --hwaccel nvenc
  python compress_video.py /path/to/folder --batch
        """,
    )
    parser.add_argument("input", nargs="?", help="Input video file or folder for batch processing")
    parser.add_argument("-o", "--output", help="Output file or directory path")
    parser.add_argument(
        "-c",
        "--codec",
        choices=["hevc", "h264", "av1", "vp9"],
        default="hevc",
        help="Target video codec (default: hevc/x265)",
    )
    parser.add_argument(
        "-p",
        "--preset",
        choices=["archival", "high", "balanced", "draft"],
        default="balanced",
        help="Compression quality profile (default: balanced)",
    )
    parser.add_argument(
        "-r",
        "--resolution",
        default="keep",
        help="Target vertical resolution (keep, 1080p, 720p, 480p, 360p)",
    )
    parser.add_argument(
        "-t",
        "--target-size",
        help="Force exact output size for WhatsApp/Discord (e.g., '10MB', '25MB')",
    )
    parser.add_argument(
        "--hwaccel",
        choices=["auto", "cpu", "nvenc", "videotoolbox", "qsv", "amf"],
        default="auto",
        help="Hardware acceleration preference (default: auto)",
    )
    parser.add_argument("--crf", type=int, help="Manual CRF value override")
    parser.add_argument(
        "--audio",
        choices=["aac", "copy", "opus", "mute"],
        default="aac",
        help="Audio handling mode (default: aac)",
    )
    parser.add_argument("--audio-bitrate", default="64k", help="Audio bitrate (default: 64k)")
    parser.add_argument("--speed", default="medium", help="CPU preset speed (ultrafast..veryslow)")
    parser.add_argument("--batch", action="store_true", help="Process all videos in input directory")

    args = parser.parse_args()

    if args.target_size:
        parsed_size = parse_size_to_bytes(args.target_size)
        if parsed_size is None:
            sys.stderr.write(
                f"[ERROR] Invalid --target-size: '{args.target_size}'. Expected format like '15MB', '25M', '500KB'.\n"
            )
            return 1

    if args.crf is not None:
        if args.crf < 0 or args.crf > 63:
            sys.stderr.write(f"[ERROR] Invalid --crf: {args.crf}. Value must be between 0 and 63.\n")
            return 1

    if not args.input:
        if sys.stdin.isatty():
            return interactive_workflow()
        parser.print_help()
        return 1
    else:
        input_path = Path(args.input)
        if not input_path.exists():
            sys.stderr.write(f"[ERROR] Input path does not exist: {input_path}\n")
            return 1

    # Batch processing
    if input_path.is_dir() or args.batch:
        video_files = [f for f in input_path.iterdir() if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS]
        if not video_files:
            print(f"[INFO] No video files found in {input_path}")
            return 0
        print(f"📦 Found {len(video_files)} videos to process in batch mode.")
        success_count = 0
        for vid in video_files:
            out_file = vid.parent / f"{vid.stem}_comp.mp4"
            if compress_video(
                input_file=vid,
                output_file=out_file,
                codec=args.codec,
                preset=args.preset,
                resolution=args.resolution,
                target_size_str=args.target_size,
                hwaccel=args.hwaccel,
                crf_override=args.crf,
                audio_mode=args.audio,
                audio_bitrate=args.audio_bitrate,
                speed_preset=args.speed,
            ):
                success_count += 1
        print(f"\n✨ Batch complete: {success_count}/{len(video_files)} videos compressed successfully.")
        return 0

    # Single file processing
    output_path = Path(args.output) if args.output else input_path.parent / f"{input_path.stem}_comp.mp4"

    success = compress_video(
        input_file=input_path,
        output_file=output_path,
        codec=args.codec,
        preset=args.preset,
        resolution=args.resolution,
        target_size_str=args.target_size,
        hwaccel=args.hwaccel,
        crf_override=args.crf,
        audio_mode=args.audio,
        audio_bitrate=args.audio_bitrate,
        speed_preset=args.speed,
    )

    return 0 if success else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.stderr.write("\n[AVISO] Operación cancelada por el usuario.\n")
        sys.exit(130)
