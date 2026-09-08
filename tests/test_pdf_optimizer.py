"""QA unit and integration tests for pdf-optimizer."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "tools" / "pdf-optimizer"))

import pikepdf
import pymupdf as fitz
from pdf_optimizer import (
    PDFStats,
    format_bytes,
    inspect_pdf,
    optimize_native,
    verify_ocr_integrity,
)


def test_format_bytes():
    """Verify byte formatting in pdf_optimizer."""
    assert format_bytes(500) == "500 B"
    assert format_bytes(2048) == "2.0 KB"
    assert format_bytes(5 * 1024 * 1024) == "5.00 MB"


def test_verify_ocr_integrity():
    """Verify OCR layer preservation checks."""
    before = PDFStats(pages=2, image_count=1, text_length=500, has_ocr=True, size_bytes=10000)

    # Intact text
    after_ok = PDFStats(pages=2, image_count=1, text_length=495, has_ocr=True, size_bytes=5000)
    assert verify_ocr_integrity(before, after_ok) is True

    # Destroyed text
    after_destroyed = PDFStats(pages=2, image_count=1, text_length=0, has_ocr=False, size_bytes=2000)
    assert verify_ocr_integrity(before, after_destroyed) is False

    # Document that had no OCR to begin with
    no_ocr_before = PDFStats(pages=1, image_count=1, text_length=5, has_ocr=False, size_bytes=10000)
    no_ocr_after = PDFStats(pages=1, image_count=1, text_length=0, has_ocr=False, size_bytes=3000)
    assert verify_ocr_integrity(no_ocr_before, no_ocr_after) is True

    # Edge case: zero text length division protection
    empty_before = PDFStats(pages=1, image_count=0, text_length=0, has_ocr=False, size_bytes=1000)
    empty_after = PDFStats(pages=1, image_count=0, text_length=0, has_ocr=False, size_bytes=500)
    assert verify_ocr_integrity(empty_before, empty_after) is True


def test_pdf_optimize_native_end_to_end():
    """End-to-end integration test creating, optimizing, and verifying a real PDF."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_pdf = Path(tmpdir) / "sample_test.pdf"
        output_pdf = Path(tmpdir) / "sample_optimized.pdf"

        # 1. Synthesize a valid PDF with text and a page
        test_text = "ESPE IT Engineering & CERN Preparation Program - Clean Code Test"
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)  # A4
        page.insert_text((50, 100), test_text, fontsize=14)
        doc.save(str(input_pdf))
        doc.close()

        assert input_pdf.exists()
        assert input_pdf.stat().st_size > 0

        # 2. Inspect original
        stats = inspect_pdf(input_pdf)
        assert stats is not None
        assert stats.pages == 1
        assert stats.has_ocr is True
        assert stats.text_length >= len(test_text)

        # 3. Optimize via native Python pipeline
        success = optimize_native(input_pdf, output_pdf, profile_key="lossless")
        assert success is True
        assert output_pdf.exists()

        # 4. Verify output PDF validity with pikepdf and PyMuPDF
        with pikepdf.open(str(output_pdf)) as pike_doc:
            assert len(pike_doc.pages) == 1

        with fitz.open(str(output_pdf)) as out_doc:
            extracted_text = out_doc[0].get_text()
            assert "CERN Preparation Program" in extracted_text


def test_inspect_and_optimize_corrupt_file():
    """Verify that corrupt or zero-byte files are handled gracefully without unhandled exceptions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Zero byte file
        zero_file = Path(tmpdir) / "empty.pdf"
        zero_file.write_bytes(b"")
        assert inspect_pdf(zero_file) is None

        # Random garbage bytes
        garbage_file = Path(tmpdir) / "garbage.pdf"
        garbage_file.write_bytes(b"\xde\xad\xbe\xef" * 100)
        assert inspect_pdf(garbage_file) is None

        # Non-existent file
        missing_file = Path(tmpdir) / "does_not_exist.pdf"
        assert inspect_pdf(missing_file) is None


def test_pdf_multipage_all_profiles():
    """Verify multi-page PDF generation, image downsampling, and all profiles."""
    import io

    from pdf_optimizer import run_single_optimization
    from PIL import Image

    with tempfile.TemporaryDirectory() as tmpdir:
        input_pdf = Path(tmpdir) / "multipage.pdf"

        # Create multi-page PDF with an image
        doc = fitz.open()
        for i in range(3):
            page = doc.new_page(width=595, height=842)
            page.insert_text((50, 50), f"Page {i + 1} - CERN & ESPE Research Notes", fontsize=12)

            # Insert an image on page 0 and page 1
            if i < 2:
                img = Image.new("RGB", (400, 300), color=(50 * (i + 1), 80, 120))
                bio = io.BytesIO()
                img.save(bio, format="PNG")
                page.insert_image(fitz.Rect(50, 100, 350, 325), stream=bio.getvalue())

        doc.save(str(input_pdf))
        doc.close()

        orig_size = input_pdf.stat().st_size
        assert orig_size > 0

        # Test each profile
        for prof in ["extreme", "lossless", "balanced", "print", "screen"]:
            out_pdf = Path(tmpdir) / f"out_{prof}.pdf"
            success = run_single_optimization(
                input_path=input_pdf,
                output_path=out_pdf,
                profile_key=prof,
                engine="native",
            )
            assert success is True
            assert out_pdf.exists()

            with fitz.open(str(out_pdf)) as out_doc:
                assert len(out_doc) == 3
                assert "CERN & ESPE Research Notes" in out_doc[0].get_text()
                assert "Page 3" in out_doc[2].get_text()


def test_pdf_encrypted_file_handling():
    """Verify that password encrypted PDFs are detected and rejected safely."""
    with tempfile.TemporaryDirectory() as tmpdir:
        enc_pdf = Path(tmpdir) / "encrypted.pdf"
        out_pdf = Path(tmpdir) / "out_enc.pdf"

        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Confidential CERN Report", fontsize=12)
        # Encrypt with password
        doc.save(
            str(enc_pdf),
            encryption=fitz.PDF_ENCRYPT_AES_256,
            owner_pw="secret123",
            user_pw="secret123",
        )
        doc.close()

        # inspect_pdf should return None gracefully
        assert inspect_pdf(enc_pdf) is None

        # optimize_native should return False gracefully
        assert optimize_native(enc_pdf, out_pdf, profile_key="balanced") is False


def test_pdf_optimize_nested_output_dir():
    """Verify that specifying an output path in a non-existent nested directory auto-creates parents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_pdf = Path(tmpdir) / "sample.pdf"
        nested_out = Path(tmpdir) / "sub1" / "sub2" / "deep_output.pdf"

        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Test nested path auto-creation", fontsize=12)
        doc.save(str(input_pdf))
        doc.close()

        assert not nested_out.parent.exists()

        success = optimize_native(input_pdf, nested_out, profile_key="lossless")
        assert success is True
        assert nested_out.exists()
        assert nested_out.parent.exists()


def test_pdf_transparent_and_masked_images_preserved():
    """Verify that images with alpha channel or masks are preserved losslessly without flattening to opaque JPEG."""
    import io

    from pdf_optimizer import run_single_optimization
    from PIL import Image

    with tempfile.TemporaryDirectory() as tmpdir:
        input_pdf = Path(tmpdir) / "transparent.pdf"
        output_pdf = Path(tmpdir) / "transparent_opt.pdf"

        # Create a PDF with text and a transparent RGBA signature image over it
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)
        page.insert_text((100, 200), "Important Academic Grade: 20.00", fontsize=16)

        # Transparent RGBA image (like a digital signature stamp)
        rgba_img = Image.new("RGBA", (200, 100), (0, 0, 0, 0))
        # Draw some non-transparent pixels
        for x in range(50, 150):
            for y in range(25, 75):
                rgba_img.putpixel((x, y), (0, 0, 180, 255))
        bio = io.BytesIO()
        rgba_img.save(bio, format="PNG")

        page.insert_image(fitz.Rect(90, 180, 290, 280), stream=bio.getvalue())
        doc.save(str(input_pdf))
        doc.close()

        # Run extreme profile (which previously flattened transparent images onto white JPEG)
        success = run_single_optimization(
            input_path=input_pdf,
            output_path=output_pdf,
            profile_key="extreme",
            engine="native",
        )
        assert success is True
        assert output_pdf.exists()

        # Verify text is intact
        with fitz.open(str(output_pdf)) as out_doc:
            text = out_doc[0].get_text()
            assert "Important Academic Grade: 20.00" in text
            # Ensure the image was not converted to DCTDecode (lossy JPEG)
            images = out_doc[0].get_images(full=True)
            assert len(images) >= 1
            for img_info in images:
                xref = img_info[0]
                base_img = out_doc.extract_image(xref)
                # Should be png / flate, not jpeg
                assert base_img["ext"] in ("png", "flate", "jpx")
