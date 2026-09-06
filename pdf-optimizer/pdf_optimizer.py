#!/usr/bin/env python3
"""
PDF Optimizer - Reducción inteligente de tamaño y preservación de texto/OCR.
Combina PyMuPDF (fitz) para inspección, pikepdf para optimización estructural
y Ghostscript para recompreión de mapa de bits.
"""

import argparse
import glob
import os
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, Optional

# Soporte UTF-8 en Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

import fitz  # PyMuPDF
import pikepdf
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

console = Console()

PROFILES: Dict[str, Dict[str, Any]] = {
    "1": {"name": "Baja (300 DPI)", "dpi": 300, "suffix": "low", "desc": "Calidad de impresión"},
    "2": {"name": "Media (150 DPI)", "dpi": 150, "suffix": "medium", "desc": "Pantallas y eBooks"},
    "3": {"name": "Alta (72 DPI)", "dpi": 72, "suffix": "high", "desc": "Máximo ahorro de espacio"}
}


def find_ghostscript() -> Optional[str]:
    """Busca automáticamente el binario de Ghostscript en rutas habituales de Windows y PATH."""
    from shutil import which
    system_gs = which("gswin64c") or which("gswin32c") or which("gs")
    if system_gs:
        return system_gs

    rutas_posibles = [
        r"C:\Program Files\gs\*\bin\gswin64c.exe",
        r"C:\Program Files (x86)\gs\*\bin\gswin32c.exe"
    ]
    for ruta in rutas_posibles:
        coincidencias = glob.glob(ruta)
        if coincidencias:
            return sorted(coincidencias, reverse=True)[0]
    return None


def analyze_pdf(input_path: Path) -> Dict[str, Any]:
    """Inspecciona páginas, imágenes y presencia de capa de texto en el PDF."""
    doc = fitz.open(str(input_path))
    total_images = 0
    has_text = False
    total_pages = len(doc)

    for page in doc:
        total_images += len(page.get_images(full=True))
        if page.get_text("text").strip():
            has_text = True

    doc.close()
    return {"pages": total_pages, "images": total_images, "has_text": has_text}


def clean_structure(input_path: Path, temp_path: Path) -> bool:
    """Limpia metadatos corruptos y comprime flujos de objetos con pikepdf."""
    try:
        with pikepdf.open(str(input_path)) as pdf:
            pdf.save(str(temp_path), object_stream_mode=pikepdf.ObjectStreamMode.generate)
        return True
    except Exception as e:
        console.print(f"[bold red]❌ Error en limpieza estructural: {e}[/bold red]")
        return False


def compress_with_gs(gs_path: str, input_path: Path, output_path: Path, dpi: int) -> bool:
    """Ejecuta Ghostscript reduciendo resolución de imágenes y manteniendo la capa OCR."""
    gs_cmd = [
        gs_path,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/default",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-dColorImageResolution={dpi}",
        f"-dGrayImageResolution={dpi}",
        "-dMonoImageResolution=300",
        "-dDownsampleColorImages=true",
        "-dDownsampleGrayImages=true",
        "-dDownsampleMonoImages=true",
        "-dColorImageDownsampleType=/Bicubic",
        "-dGrayImageDownsampleType=/Bicubic",
        "-dMonoImageDownsampleType=/Subsample",
        "-dDetectDuplicateImages=true",
        "-dCompressFonts=true",
        "-dSubsetFonts=true",
        "-dAutoRotatePages=/None",
        f"-sOutputFile={output_path}",
        str(input_path)
    ]
    try:
        subprocess.run(gs_cmd, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def optimize_file(gs_path: str, file_path: Path, profile_key: str = "2") -> Optional[Path]:
    """Ejecuta el ciclo de optimización sobre un único archivo."""
    profile = PROFILES[profile_key]
    original_size = file_path.stat().st_size

    temp_struct = file_path.parent / f"temp_struct_{file_path.stem}.pdf"
    output_path = file_path.parent / f"{file_path.stem}_compressed_{profile['suffix']}.pdf"

    console.print(f"\n[bold blue]🔍 Analizando: {file_path.name}...[/bold blue]")
    stats = analyze_pdf(file_path)
    console.print(f"📄 Páginas: [cyan]{stats['pages']}[/cyan] | 🖼️ Imágenes: [cyan]{stats['images']}[/cyan] | 🔤 Texto/OCR: [cyan]{'Sí' if stats['has_text'] else 'No'}[/cyan]")

    if not clean_structure(file_path, temp_struct):
        return None

    success = compress_with_gs(gs_path, temp_struct, output_path, profile["dpi"])
    if temp_struct.exists():
        temp_struct.unlink()

    if not success or not output_path.exists():
        console.print("[bold red]❌ Error durante la recompresión con Ghostscript.[/bold red]")
        return None

    final_size = output_path.stat().st_size
    saved_bytes = original_size - final_size

    table = Table(title="Resultados de la Optimización")
    table.add_column("Métrica", justify="left", style="cyan")
    table.add_column("Valor", justify="right", style="green")
    table.add_row("Peso Original", f"{original_size / (1024*1024):.2f} MB")
    table.add_row("Peso Final", f"{final_size / (1024*1024):.2f} MB")

    if saved_bytes > 0:
        saved_pct = (saved_bytes / original_size) * 100
        table.add_row("Espacio Ahorrado", f"{saved_pct:.1f}%")
        console.print(table)
        console.print(f"\n[bold green]✅ Guardado en:[/bold green] {output_path.name}\n")
        return output_path
    else:
        output_path.unlink()
        console.print(table)
        console.print("\n[bold yellow]⚠️ El archivo original ya estaba altamente optimizado. Se canceló la creación para evitar pérdida de calidad innecesaria.[/bold yellow]\n")
        return None


def run_interactive(gs_path: str) -> None:
    """Modo de ejecución interactivo con Tkinter y menús en consola."""
    from tkinter import Tk
    from tkinter.filedialog import askopenfilename

    root = Tk()
    root.withdraw()

    while True:
        root.attributes("-topmost", True)
        selected_file = askopenfilename(
            title="Selecciona el PDF a optimizar",
            filetypes=[("Archivos PDF", "*.pdf")]
        )

        if not selected_file:
            console.print("\n[yellow]⚠️ No se seleccionó ningún archivo.[/yellow]")
            break

        pdf_path = Path(selected_file)

        console.print("\nSelecciona el nivel de compresión:")
        for key, p in PROFILES.items():
            console.print(f"  [bold cyan]{key}.[/bold cyan] {p['name']} ({p['desc']})")

        choice = Prompt.ask("Elige una opción", choices=list(PROFILES.keys()), default="2")
        optimize_file(gs_path, pdf_path, choice)

        cont = Prompt.ask("\n¿Deseas optimizar otro documento?", choices=["s", "n"], default="n")
        if cont.lower() != "s":
            break

    root.destroy()


def main() -> None:
    parser = argparse.ArgumentParser(description="PDF Optimizer - Optimización inteligente de PDFs.")
    parser.add_argument("-i", "--input", type=str, default=None, help="Ruta al PDF a optimizar.")
    parser.add_argument("-p", "--profile", type=str, default="2", choices=["1", "2", "3"], help="Perfil: 1=Baja (300 DPI), 2=Media (150 DPI), 3=Alta (72 DPI).")

    args = parser.parse_args()

    gs_path = find_ghostscript()
    if not gs_path:
        console.print("[bold red]❌ No se encontró Ghostscript en el sistema. Asegúrate de tenerlo instalado y en el PATH.[/bold red]")
        sys.exit(1)

    if args.input:
        target = Path(args.input)
        if not target.exists():
            console.print(f"[bold red]❌ El archivo no existe: {target}[/bold red]")
            sys.exit(1)
        optimize_file(gs_path, target, args.profile)
    else:
        run_interactive(gs_path)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario.")
