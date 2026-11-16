"""Evidence-oriented tests for the revised 'best for this goal' selectors."""
from pathlib import Path
import sys
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from processing import (
    arithmetic, decode_image, denoise, eliminate_channels, histogram_enhancement,
    recommend_arithmetic, recommend_channel, recommend_denoise, recommend_histogram,
    recommend_sharpen, recommend_solarization, sharpening,
)
from ui_style import theme_css

SAMPLES = Path(__file__).resolve().parents[1] / "assets" / "samples"

def sample(prefix):
    found = list(SAMPLES.glob(f"{prefix}*"))
    assert len(found) == 1
    return decode_image(found[0].read_bytes())


def test_arithmetic_dark_sample_has_explainable_brighten_candidate():
    image = sample("03_")
    report = recommend_arithmetic(image, arithmetic(image), "Auto")
    assert report.operation in ("Addition (+)", "Multiplication (*)")
    assert "Brighten" in report.goal and "median" in report.basis
    assert len(report.rows) == 4 and "New saturation (%)" in report.rows[0]
    assert report.evidence and report.limitation
    chosen = next(x for x in report.rows if x["Operation"] == report.operation)
    assert chosen["Score (lower is better)"] == min(
        x["Score (lower is better)"] for x in report.rows if x["Eligible"] == "Yes"
    )


def test_arithmetic_overbright_and_balanced_do_not_auto_brighten():
    gradient = np.tile(np.arange(80, 201, dtype=np.uint8), (64, 1))
    neutral = np.stack([gradient]*3, axis=-1)
    assert recommend_arithmetic(neutral, arithmetic(neutral)).operation is None
    bright = np.clip(neutral.astype(int) + 70, 0, 255).astype(np.uint8)
    rec = recommend_arithmetic(bright, arithmetic(bright), "Auto")
    assert rec.operation in ("Subtraction (-)", "Division (/)")
    assert "Darken" in rec.goal
    assert recommend_arithmetic(neutral, arithmetic(neutral), "Brighten").operation in (
        "Addition (+)", "Multiplication (*)"
    )


def test_arithmetic_flat_image_does_not_claim_restored_details():
    solid = np.full((50, 60, 3), 15, np.uint8)
    assert recommend_arithmetic(solid, arithmetic(solid)).operation is None


def test_solarization_is_goal_match_not_quality_claim():
    image = sample("04_")
    selective = recommend_solarization(image, 128, "Selective highlight inversion")
    assert selective.operation == "Solarization"
    assert "4.1%" in selective.reason
    assert "not a proof" in selective.limitation
    full = recommend_solarization(image, 128, "Full color inversion")
    assert full.operation == "Complementary"
    none = recommend_solarization(image, 255, "Selective highlight inversion")
    assert none.operation is None


def test_channel_diagnostic_disclaims_actual_color_correction():
    blue_cast = sample("05_")
    r = recommend_channel(blue_cast)
    assert r.operation == "Remove Blue"
    assert "not proof" in r.limitation
    assert len(r.rows) == 3
    neutral = np.tile(np.arange(80, 120, dtype=np.uint8), (50, 1))
    neutral = np.stack([neutral]*3, axis=-1)
    assert recommend_channel(neutral).operation is None


def test_histogram_recommendation_uses_measured_extremes():
    x = sample("06_")
    report = recommend_histogram(histogram_enhancement(x))
    assert report.operation == "Stretching"
    assert report.rows[0]["Near-extreme pixels (%)"] < report.rows[1]["Near-extreme pixels (%)"]
    assert "Contrast gain" in report.rows[0]
    assert report.limitation
    uniform = np.full((40, 40, 3), 90, np.uint8)
    assert recommend_histogram(histogram_enhancement(uniform)).operation is None


def test_denoise_rank_is_highest_measured_snr_and_zero_noise_has_no_winner():
    image = sample("07_")
    out = denoise(image)
    rec = recommend_denoise(image, out)
    assert rec.operation == "Median Filter"
    highest = max(rec.rows, key=lambda row: row["SNR (dB)"])
    assert highest["Method"] == rec.operation
    no_noise = denoise(image, density=0)
    assert recommend_denoise(image, no_noise).operation is None


def test_sharpen_only_wins_when_reference_fidelity_improves():
    image = sample("08_")
    rec = recommend_sharpen(image, sharpening(image))
    assert rec.operation == "Custom Sharpening"
    assert rec.rows[1]["PSNR (dB)"] > rec.rows[0]["PSNR (dB)"]
    flat = np.full((32, 32, 3), 110, np.uint8)
    assert recommend_sharpen(flat, sharpening(flat)).operation is None


def test_css_switch_has_explicit_light_and_dark_tokens_and_icon_style():
    dark, light = theme_css(True), theme_css(False)
    assert "#081321" in dark and "#F5F8FD" in light
    for css in (dark, light):
        for element in ('stFileUploaderDropzone','stSidebarContent','stSelectbox','stDataFrame','stRadio'):
            assert element in css
        assert ".st-key-theme_toggle" in css
        assert "--ip-surface" in css
