"""QA unit tests for video-compressor modules and algorithms."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "tools" / "video-compressor"))

from compress_video import (
    VideoMetadata,
    build_scale_filter,
    format_bytes,
    parse_size_to_bytes,
    select_best_encoder,
)


def test_parse_size_to_bytes_valid():
    """Verify parsing of various standard size units."""
    assert parse_size_to_bytes("10MB") == 10 * 1024 * 1024
    assert parse_size_to_bytes("25M") == 25 * 1024 * 1024
    assert parse_size_to_bytes("500KB") == 500 * 1024
    assert parse_size_to_bytes("1.5GB") == int(1.5 * 1024 * 1024 * 1024)
    # Default without unit is MB
    assert parse_size_to_bytes("20") == 20 * 1024 * 1024
    # Spaces and case insensitivity
    assert parse_size_to_bytes("  15 mb  ") == 15 * 1024 * 1024


def test_parse_size_to_bytes_invalid():
    """Verify that invalid strings, zero, and negative values return None."""
    assert parse_size_to_bytes("0MB") is None
    assert parse_size_to_bytes("-10MB") is None
    assert parse_size_to_bytes("abc") is None
    assert parse_size_to_bytes("") is None
    assert parse_size_to_bytes("   ") is None


def test_format_bytes():
    """Verify human-readable byte formatting."""
    assert format_bytes(500 * 1024) == "0.49 MB"
    assert format_bytes(10 * 1024 * 1024) == "10.00 MB"
    assert format_bytes(2 * 1024 * 1024 * 1024) == "2.00 GB"


def test_build_scale_filter():
    """Verify even-dimension safe scale filter generation."""
    dummy_meta = VideoMetadata(
        duration_sec=60.0,
        width=1920,
        height=1080,
        bitrate_kbps=5000.0,
        video_codec="h264",
        audio_codec="aac",
        size_bytes=100000,
    )
    # Keep original dimensions, still ensure divisible by 2
    assert "trunc" in build_scale_filter("keep", dummy_meta)
    assert "trunc" in build_scale_filter("original", dummy_meta)

    # Scale down to 720p
    assert build_scale_filter("720p", dummy_meta) == "scale=-2:720"
    assert build_scale_filter("480p", dummy_meta) == "scale=-2:480"

    # Avoid upscaling smaller videos
    small_meta = VideoMetadata(
        duration_sec=10.0,
        width=640,
        height=360,
        bitrate_kbps=1000.0,
        video_codec="h264",
        audio_codec="aac",
        size_bytes=10000,
    )
    assert "trunc" in build_scale_filter("720p", small_meta)


def test_select_best_encoder():
    """Verify encoder selection and hardware fallback logic."""
    # Forced CPU
    enc, label = select_best_encoder("hevc", "cpu", {"hevc_nvenc", "libx265"})
    assert enc == "libx265"
    assert label == "cpu"

    # Hardware detection (NVIDIA NVENC)
    enc, label = select_best_encoder("hevc", "auto", {"hevc_nvenc", "libx265"})
    assert enc == "hevc_nvenc"
    assert "NVIDIA" in label

    # Hardware fallback to CPU when no GPU encoders are available
    enc, label = select_best_encoder("hevc", "auto", {"libx265"})
    assert enc == "libx265"
    assert "CPU" in label

    # AV1 selection
    enc, label = select_best_encoder("av1", "cpu", set())
    assert enc == "libsvtav1"


def test_all_codecs_cpu_defaults():
    """Verify default CPU encoders for all supported codecs."""
    expected = {
        "hevc": "libx265",
        "h264": "libx264",
        "av1": "libsvtav1",
        "vp9": "libvpx-vp9",
    }
    for codec, expected_enc in expected.items():
        enc, label = select_best_encoder(codec, "cpu", set())
        assert enc == expected_enc
        assert label == "cpu"


def test_hardware_encoders_priority():
    """Verify Apple, Intel, and AMD hardware acceleration mapping."""
    # Apple VideoToolbox
    enc, label = select_best_encoder("hevc", "auto", {"hevc_videotoolbox"})
    assert enc == "hevc_videotoolbox"
    assert "Apple" in label

    # Intel QuickSync
    enc, label = select_best_encoder("h264", "auto", {"h264_qsv"})
    assert enc == "h264_qsv"
    assert "Intel" in label

    # AMD AMF
    enc, label = select_best_encoder("h264", "auto", {"h264_amf"})
    assert enc == "h264_amf"
    assert "AMD" in label


def test_format_bytes_edge_cases():
    """Verify boundary and large size formatting."""
    assert format_bytes(0) == "0.00 MB"
    assert format_bytes(50 * 1024 * 1024 * 1024) == "50.00 GB"


def test_video_metadata_silent_handling():
    """Verify VideoMetadata structure and that missing audio is properly represented."""
    meta = VideoMetadata(
        duration_sec=30.0,
        width=1280,
        height=720,
        bitrate_kbps=2500.0,
        video_codec="h264",
        audio_codec=None,
        size_bytes=9375000,
    )
    assert meta.audio_codec is None
    assert meta.duration_sec == 30.0


def test_compress_video_invalid_target_size_cli(tmp_path):
    """Passing an invalid target-size string must be caught and rejected with code 1."""
    fake_vid = tmp_path / "test.mp4"
    fake_vid.write_bytes(b"fake data")

    import subprocess
    import sys

    script = Path(__file__).resolve().parent.parent / "tools" / "video-compressor" / "compress_video.py"
    proc = subprocess.run(
        [sys.executable, str(script), str(fake_vid), "--target-size", "invalid_size_str"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    assert "Invalid --target-size" in proc.stderr


def test_compress_video_invalid_crf_cli(tmp_path):
    """Passing an out-of-bounds CRF value must be rejected with code 1."""
    fake_vid = tmp_path / "test.mp4"
    fake_vid.write_bytes(b"fake data")

    import subprocess
    import sys

    script = Path(__file__).resolve().parent.parent / "tools" / "video-compressor" / "compress_video.py"
    proc = subprocess.run(
        [sys.executable, str(script), str(fake_vid), "--crf", "100"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    assert "Invalid --crf" in proc.stderr
