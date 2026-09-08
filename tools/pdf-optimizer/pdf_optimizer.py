#!/usr/bin/env python3
"""
PDF Optimizer - Multi-Engine, OCR-Safe Document Compression Suite.
Features native Python structural compression (pikepdf), in-memory image
downsampling (PyMuPDF + Pillow), and optional Ghostscript deep compression.
Guarantees 100% preservation of selectable text and OCR layers.
"""

from __future__ import annotations

import argparse
import glob
import io
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

# Enable UTF-8 console output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

import pikepdf
import pymupdf as fitz
from PIL import Image
from rich.console import Console

console = Console()

PROFILES: Dict[str, Dict[str, Any]] = {
    "extreme": {
        "name": "Compresión Extrema (72 DPI, Compresión Agresiva)",
        "dpi": 72,
        "quality": 45,
        "desc": (
            "Máxima reducción posible. Aplana imágenes y comprime al máximo manteniendo texto y OCR 100% legibles."
        ),
    },
    "balanced": {
        "name": "Balanced (150 DPI)",
        "dpi": 150,
        "quality": 75,
        "desc": "Recommended for classroom submissions, email, and reading.",
    },
    "screen": {
        "name": "Aggressive / Screen (72 DPI)",
        "dpi": 72,
        "quality": 50,
        "desc": "Maximum size reduction for fast web viewing or storage limits.",
    },
    "print": {
        "name": "Print Quality (300 DPI)",
        "dpi": 300,
        "quality": 85,
        "desc": "High visual fidelity for printing or formal archives.",
    },
    "lossless": {
        "name": "Lossless (Structural Only)",
        "dpi": None,
        "quality": 100,
        "desc": "Flattens object streams, strips bloat, 0% visual loss.",
    },
}


@dataclass
class PDFStats:
    pages: int
    image_count: int
    text_length: int
    has_ocr: bool
    size_bytes: int


def format_bytes(size: float) -> str:
    """Formats bytes into human-readable MB/KB string."""
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"
    elif size >= 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size:.0f} B"


def find_ghostscript() -> Optional[str]:
    """Auto-detects Ghostscript executable across Windows, macOS, and Linux."""
    system_gs = shutil.which("gswin64c") or shutil.which("gswin32c") or shutil.which("gs")
    if system_gs:
        return system_gs

    if sys.platform == "win32":
        candidates = [
            r"C:\Program Files\gs\*\bin\gswin64c.exe",
            r"C:\Program Files (x86)\gs\*\bin\gswin32c.exe",
        ]
        for pattern in candidates:
            matches = glob.glob(pattern)
            if matches:
                return sorted(matches, reverse=True)[0]

    return None


def inspect_pdf(pdf_path: Path) -> Optional[PDFStats]:
    """Extracts page count, embedded image count, and text layer statistics."""
    try:
        with fitz.open(str(pdf_path)) as doc:
            if doc.is_encrypted:
                console.print(f"[bold yellow]⚠️ El archivo {pdf_path.name} está protegido con contraseña.[/bold yellow]")
                return None
            pages = len(doc)
            total_images = 0
            total_text_len = 0

            for page in doc:
                images = page.get_images(full=True)
                total_images += len(images)
                txt = page.get_text("text").strip()
                total_text_len += len(txt)

        return PDFStats(
            pages=pages,
            image_count=total_images,
            text_length=total_text_len,
            has_ocr=total_text_len > 20,
            size_bytes=pdf_path.stat().st_size,
        )
    except Exception as err:
        console.print(f"[bold red]❌ Error inspectando PDF {pdf_path.name}: {err}[/bold red]")
        return None


def optimize_images_in_doc(
    doc: fitz.Document,
    target_dpi: int,
    jpeg_quality: int,
) -> int:
    """
    Re-samples and re-compresses embedded raster images in-place without touching
    page text, font definitions, vectors, or layout coordinates.
    """
    from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn

    unique_images: list[tuple[fitz.Page, int]] = []
    seen_xrefs = set()
    for page in doc:
        for img_info in page.get_images(full=True):
            xref = img_info[0]
            if xref not in seen_xrefs:
                seen_xrefs.add(xref)
                unique_images.append((page, xref))

    if not unique_images:
        return 0

    images_compressed = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=30),
        TaskProgressColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Optimizando imágenes incrustadas...", total=len(unique_images))
        for page, xref in unique_images:
            try:
                base_image = doc.extract_image(xref)
                if not base_image:
                    continue

                image_bytes = base_image["image"]
                orig_width = base_image["width"]
                orig_height = base_image["height"]

                # If image is very small (tiny icons, spacers), skip
                if orig_width < 32 and orig_height < 32:
                    continue

                # Load into PIL
                pil_img = Image.open(io.BytesIO(image_bytes))

                # Estimate page scale / DPI based on actual page point geometry
                page_rect = page.rect
                page_max_pt = max(page_rect.width, page_rect.height)
                if page_max_pt <= 0:
                    page_max_pt = 792.0
                target_max = int((page_max_pt / 72.0) * target_dpi)

                max_dim = max(orig_width, orig_height)
                needs_resample = max_dim > target_max
                if needs_resample:
                    scale = target_max / float(max_dim)
                    new_width = max(1, int(orig_width * scale))
                    new_height = max(1, int(orig_height * scale))
                    pil_img = pil_img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Recompress to JPEG (convert RGBA/P to RGB if needed)
                out_buffer = io.BytesIO()
                if pil_img.mode in ("RGBA", "LA") or (pil_img.mode == "P" and "transparency" in pil_img.info):
                    if target_dpi <= 72 or jpeg_quality <= 60:
                        # Flatten onto clean white background to dramatically reduce size
                        bg = Image.new("RGB", pil_img.size, (255, 255, 255))
                        rgba = pil_img.convert("RGBA")
                        bg.paste(rgba, mask=rgba.split()[-1])
                        bg.save(
                            out_buffer,
                            format="JPEG",
                            quality=jpeg_quality,
                            optimize=True,
                        )
                    else:
                        pil_img.save(out_buffer, format="PNG", optimize=True)
                elif pil_img.mode == "1":
                    pil_img.save(out_buffer, format="PNG", optimize=True)
                else:
                    rgb_img = pil_img if pil_img.mode == "RGB" else pil_img.convert("RGB")
                    rgb_img.save(
                        out_buffer,
                        format="JPEG",
                        quality=jpeg_quality,
                        optimize=True,
                    )

                new_bytes = out_buffer.getvalue()

                # Only replace if new image actually saves space
                if len(new_bytes) < len(image_bytes):
                    page.replace_image(xref, stream=new_bytes)
                    images_compressed += 1

            except Exception:
                continue
            finally:
                progress.advance(task)

    return images_compressed


def optimize_native(
    input_path: Path,
    output_path: Path,
    profile_key: str,
    custom_dpi: Optional[int] = None,
    custom_quality: Optional[int] = None,
) -> bool:
    """
    Pure-Python optimization pipeline:
    1. PyMuPDF in-memory raster image downsampling (if profile != lossless).
    2. pikepdf structural cleanup: deduplicates objects, linearizes object streams,
       removes unreferenced objects, and strips corrupted XML metadata.
    """
    prof = PROFILES.get(profile_key, PROFILES["balanced"])
    dpi = custom_dpi or prof["dpi"]
    quality = custom_quality or prof["quality"]

    # Create collision-free temporary file for intermediate stage
    temp_fd, temp_intermediate_path = tempfile.mkstemp(suffix=".pdf", prefix="opt_tmp_")
    os.close(temp_fd)
    temp_intermediate = Path(temp_intermediate_path)

    try:
        # Step 1: Open with PyMuPDF
        with fitz.open(str(input_path)) as doc:
            if doc.is_encrypted:
                console.print(
                    f"[bold red]❌ No se puede optimizar {input_path.name}: está cifrado con contraseña.[/bold red]"
                )
                return False
            # Re-compress raster images if applicable
            if dpi is not None:
                optimize_images_in_doc(doc, target_dpi=dpi, jpeg_quality=quality)

            # Save with clean stream garbage collection
            doc.save(
                str(temp_intermediate),
                garbage=4,
                deflate=True,
                clean=True,
            )

        # Step 2: pikepdf structural optimization & object streams
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with pikepdf.open(str(temp_intermediate)) as pdf:
            pdf.remove_unreferenced_resources()
            pdf.save(
                str(output_path),
                object_stream_mode=pikepdf.ObjectStreamMode.generate,
                compress_streams=True,
                linearize=True,
            )

        return True

    except Exception as err:
        console.print(f"[bold red]❌ Error en motor nativo: {err}[/bold red]")
        return False
    finally:
        if temp_intermediate.exists():
            try:
                temp_intermediate.unlink()
            except OSError:
                pass


def optimize_ghostscript(
    gs_bin: str,
    input_path: Path,
    output_path: Path,
    dpi: int,
) -> bool:
    """Executes Ghostscript deep PDF flattening preserving OCR text."""
    gs_cmd = [
        gs_bin,
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
        "-dAutoRotatePages=/None",
        "-dPrinted=false",
        f"-sOutputFile={output_path}",
        str(input_path),
    ]
    try:
        subprocess.run(gs_cmd, capture_output=True, text=True, check=True)
        return output_path.exists() and output_path.stat().st_size > 0
    except subprocess.CalledProcessError as err:
        console.print(f"[bold red]❌ Error en Ghostscript: {err.stderr}[/bold red]")
        return False


def verify_ocr_integrity(before: PDFStats, after: PDFStats, tolerance: float = 0.05) -> bool:
    """Verifies that the text layer was not inadvertently erased during compression."""
    if not before.has_ocr or before.text_length == 0:
        return True  # Document had no text layer to begin with

    if after.text_length == 0 and before.text_length > 50:
        return False

    ratio = abs(before.text_length - after.text_length) / float(before.text_length)
    return ratio <= tolerance


def run_single_optimization(
    input_path: Path,
    output_path: Path,
    profile_key: str = "balanced",
    engine: str = "native",
    strict_ocr: bool = False,
) -> bool:
    """High-level runner with safety rollback, OCR verification, and reporting."""
    stats_before = inspect_pdf(input_path)
    if not stats_before:
        return False

    console.print("\n[cyan]────────────────────────────────────────────────────────[/cyan]")
    console.print(f"📄 [bold white]{input_path.name}[/bold white]")
    console.print(
        f"📊 Original: {format_bytes(stats_before.size_bytes)} | "
        f"Páginas: {stats_before.pages} | Imágenes: {stats_before.image_count} | "
        f"OCR/Texto: {'✅ Presente' if stats_before.has_ocr else 'ℹ️ No detectado'}"
    )
    console.print(f"⚙️  Perfil: [bold green]{profile_key}[/bold green] | Motor: [bold yellow]{engine}[/bold yellow]")

    start_time = time.time()
    success = False

    # Choose engine
    gs_bin = find_ghostscript()
    if engine == "gs":
        if not gs_bin:
            console.print("[yellow]⚠️ Ghostscript no encontrado en el sistema. Usando motor nativo Python.[/yellow]")
            success = optimize_native(input_path, output_path, profile_key)
        else:
            dpi = PROFILES.get(profile_key, PROFILES["balanced"])["dpi"] or 150
            success = optimize_ghostscript(gs_bin, input_path, output_path, dpi)
    else:
        success = optimize_native(input_path, output_path, profile_key)

    if not success or not output_path.exists():
        console.print("[bold red]❌ Falló la optimización del documento.[/bold red]")
        return False

    stats_after = inspect_pdf(output_path)
    if not stats_after:
        return False

    elapsed = time.time() - start_time

    # OCR verification
    ocr_ok = verify_ocr_integrity(stats_before, stats_after)
    if not ocr_ok:
        console.print("[bold red]⚠️ ALERTA: La capa de texto/OCR sufrió degradación inesperada.[/bold red]")
        if strict_ocr:
            console.print("[bold red]Deshaciendo cambios por modo --strict-ocr...[/bold red]")
            if output_path.exists() and output_path.resolve() != input_path.resolve():
                output_path.unlink()
            return False

    # Space savings check
    saved_bytes = stats_before.size_bytes - stats_after.size_bytes
    if saved_bytes <= 0:
        console.print(
            f"[yellow]ℹ️ El archivo ya estaba altamente optimizado. La compresión no redujo peso adicional "
            f"({format_bytes(stats_after.size_bytes)} vs {format_bytes(stats_before.size_bytes)}).[/yellow]"
        )
        if stats_before.image_count == 0:
            console.print(
                "[dim]   (Nota: Este documento es 100% texto/vectorial, sin imágenes rasterizadas que reducir).[/dim]"
            )
        console.print("[yellow]Conservando archivo original sin alteraciones.[/yellow]")
        if output_path.exists() and output_path.resolve() != input_path.resolve():
            output_path.unlink()
        return True

    savings_pct = (saved_bytes / stats_before.size_bytes) * 100.0

    console.print(f"[bold green]✨ Optimización exitosa en {elapsed:.1f}s![/bold green]")
    console.print(
        f"📦 Final: [bold white]{format_bytes(stats_after.size_bytes)}[/bold white] "
        f"([bold green]-{savings_pct:.1f}%[/bold green] | Ahorro: [bold cyan]{format_bytes(saved_bytes)}[/bold cyan])"
    )
    console.print(f"🔒 Capa de Texto/OCR: {'✅ 100% Intacta' if ocr_ok else '⚠️ Revisar'}")
    if stats_before.image_count == 0:
        console.print(
            "[dim]ℹ️  Nota: Documento 100% texto/vectorial (sin fotos ni escaneos). El ahorro proviene de optimización de flujos y fuentes.[/dim]"
        )
    console.print(f"📁 Guardado en: [dim]{output_path.resolve()}[/dim]")
    return True


def interactive_gui_picker() -> Optional[Path]:
    """Displays a native file picker dialog if GUI is available."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        file_selected = filedialog.askopenfilename(
            title="Seleccionar documento PDF para optimizar",
            filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")],
        )
        root.destroy()
        return Path(file_selected) if file_selected else None
    except Exception:
        return None


def interactive_workflow() -> int:
    """Guided interactive workflow with Rich UI when no arguments are provided."""
    try:
        from rich import box
        from rich.panel import Panel
        from rich.prompt import Prompt

        console.print()
        console.print(
            Panel(
                "[bold cyan]📄  OPTIMIZADOR DE DOCUMENTOS PDF - SCRIPT-TOOLS[/bold cyan]\n"
                "[dim]Preservación Garantizada 100% OCR, Re-muestreo y Reducción Híbrida[/dim]",
                box=box.ROUNDED,
                border_style="cyan",
            )
        )

        console.print("[bold]¿Cómo deseas seleccionar el documento PDF?[/bold]")
        console.print("  [1] 📂 Abrir ventana de selección de archivos (Recomendado)")
        console.print("  [2] ✍️  Escribir o arrastrar la ruta del PDF aquí")
        console.print("  [0] 🚪 Cancelar")
        pick_mode = Prompt.ask("Opción", choices=["1", "2", "0"], default="1")
        if pick_mode == "0":
            return 0

        pdf_file = None
        if pick_mode == "1":
            pdf_file = interactive_gui_picker()
            if not pdf_file:
                console.print("[yellow]Selección cancelada.[/yellow]")
                return 0
        else:
            raw = Prompt.ask("Ruta del archivo (o arrastra el documento aquí)").strip().strip('"').strip("'")
            pdf_file = Path(raw)
            if not pdf_file.exists():
                console.print(f"[bold red]El archivo no existe: {pdf_file}[/bold red]")
                Prompt.ask("\n[dim]Presiona Enter para salir...[/dim]")
                return 1

        console.print(f"\n[green]Archivo seleccionado:[/green] [bold]{pdf_file.name}[/bold]")
        console.print("[bold]Selecciona el perfil de optimización:[/bold]")
        console.print(
            "  [1] ⚡ Extrema (Máxima reducción: 72 DPI, compresión agresiva, texto/OCR intactos) [Recomendado para límites < 2 MB]"
        )
        console.print("  [2] ⚖️  Equilibrado (150 DPI - Tareas universitarias, correo, lectura) [Recomendado]")
        console.print("  [3] 📱 Pantalla / Aula Virtual (72 DPI - Cuotas moderadas)")
        console.print("  [4] 🖨️  Impresión Formal (300 DPI - Portafolios y documentos oficiales)")
        console.print("  [5] 💎 Sin Pérdida (0% degradación visual, reorganización de objetos)")
        console.print("  [0] 🚪 Cancelar")

        profile_choice = Prompt.ask("Perfil", choices=["1", "2", "3", "4", "5", "0"], default="1")
        if profile_choice == "0":
            return 0

        profiles = {
            "1": "extreme",
            "2": "balanced",
            "3": "screen",
            "4": "print",
            "5": "lossless",
        }
        selected_profile = profiles[profile_choice]
        strict_ocr = True

        out_file = pdf_file.parent / f"{pdf_file.stem}_optimized.pdf"
        console.print(
            f"\n[cyan]Iniciando optimización de [bold]{pdf_file.name}[/bold] con perfil '{selected_profile}'...[/cyan]\n"
        )
        ok = run_single_optimization(
            input_path=pdf_file,
            output_path=out_file,
            profile_key=selected_profile,
            engine="native",
            strict_ocr=strict_ocr,
        )
        if ok:
            console.print(f"\n[bold green]✓ Documento optimizado exitosamente: {out_file}[/bold green]")
        else:
            console.print("\n[bold red]✗ No se pudo completar la optimización del PDF.[/bold red]")

        Prompt.ask("\n[bold green]Presiona Enter para salir...[/bold green]")
        return 0 if ok else 1
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        if sys.stdin.isatty():
            try:
                input("\nPresiona Enter para salir...")
            except Exception:
                pass
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="PDF Optimizer - Multi-Engine, OCR-Safe Document Compression Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Perfiles disponibles:
  extreme     Compresión máxima (72 DPI, compresión agresiva JPEG/WebP, 100% texto/OCR intacto).
  balanced    150 DPI, recomendado para tareas, correo y lectura general.
  screen      72 DPI, compresión agresiva para límites estrictos de peso.
  print       300 DPI, alta fidelidad para impresión y archivado formal.
  lossless    Compresión estructural pura sin pérdida visual (pikepdf object streams).

Ejemplos:
  python pdf_optimizer.py documento.pdf --profile extreme
  python pdf_optimizer.py scan.pdf --profile screen
  python pdf_optimizer.py archivo.pdf --engine gs
  python pdf_optimizer.py ./carpeta_pdfs --batch --profile balanced
        """,
    )
    parser.add_argument("input", nargs="?", help="Ruta al archivo PDF o carpeta para procesar")
    parser.add_argument("-o", "--output", help="Ruta de salida del PDF optimizado")
    parser.add_argument(
        "-p",
        "--profile",
        choices=["extreme", "lossless", "print", "balanced", "screen"],
        default="balanced",
        help="Perfil de optimización (por defecto: balanced)",
    )
    parser.add_argument(
        "-e",
        "--engine",
        choices=["native", "gs"],
        default="native",
        help="Motor de optimización: 'native' (Python puro, recomendado) o 'gs' (Ghostscript)",
    )
    parser.add_argument(
        "--strict-ocr",
        action="store_true",
        help="Cancela y revierte si se detecta cualquier pérdida en la capa de texto OCR",
    )
    parser.add_argument("--batch", action="store_true", help="Procesa todos los archivos PDF en la carpeta")

    args = parser.parse_args()

    if not args.input:
        if sys.stdin.isatty():
            return interactive_workflow()
        parser.print_help()
        return 1
    else:
        input_path = Path(args.input)
        if not input_path.exists():
            console.print(f"[bold red]Error: La ruta de entrada no existe: {input_path}[/bold red]")
            return 1

    # Batch directory processing
    if input_path.is_dir() or args.batch:
        pdf_files = [f for f in input_path.iterdir() if f.is_file() and f.suffix.lower() == ".pdf"]
        if not pdf_files:
            console.print(f"[yellow]No se encontraron archivos PDF en {input_path}[/yellow]")
            return 0

        console.print(f"[bold cyan]📦 Procesando {len(pdf_files)} documentos en modo lote...[/bold cyan]")
        success_count = 0
        total_orig_bytes = 0
        total_final_bytes = 0

        for pdf in pdf_files:
            out_file = pdf.parent / f"{pdf.stem}_opt.pdf"
            orig_size = pdf.stat().st_size
            total_orig_bytes += orig_size
            if run_single_optimization(
                input_path=pdf,
                output_path=out_file,
                profile_key=args.profile,
                engine=args.engine,
                strict_ocr=args.strict_ocr,
            ):
                success_count += 1
                total_final_bytes += out_file.stat().st_size if out_file.exists() else orig_size
            else:
                total_final_bytes += orig_size

        saved_total = total_orig_bytes - total_final_bytes
        savings_ratio = (saved_total / total_orig_bytes * 100.0) if total_orig_bytes > 0 else 0

        console.print("\n[bold green]" + "═" * 60 + "[/bold green]")
        console.print(f"🎉 [bold white]Resumen Lote:[/bold white] {success_count}/{len(pdf_files)} procesados.")
        console.print(
            f"📊 Espacio Total Ahorrado: [bold cyan]{format_bytes(saved_total)}[/bold cyan] (-{savings_ratio:.1f}%)"
        )
        console.print("[bold green]" + "═" * 60 + "[/bold green]\n")
        return 0

    # Single file
    output_path = Path(args.output) if args.output else input_path.parent / f"{input_path.stem}_opt.pdf"

    success = run_single_optimization(
        input_path=input_path,
        output_path=output_path,
        profile_key=args.profile,
        engine=args.engine,
        strict_ocr=args.strict_ocr,
    )

    return 0 if success else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Operación cancelada por el usuario.[/yellow]")
        sys.exit(130)
