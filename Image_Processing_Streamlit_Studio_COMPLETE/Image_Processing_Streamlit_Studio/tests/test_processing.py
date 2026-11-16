"""Regression tests for every practical part of the final executed Colab notebook."""
from pathlib import Path
import sys

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from processing import (
    add_salt_pepper, arithmetic, brightness_stats, custom_grayscale, decode_image,
    denoise, edge_detection, eliminate_channels, encode_png, histogram_enhancement,
    psnr, recommend_arithmetic, recommend_channel, recommend_denoise,
    recommend_histogram, recommend_sharpen, recommendation_for, rgb_channels,
    sharpening, snr, solarization,
)

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "assets" / "samples"
FILES = [
    "01_T1_RGB_Separation_Coffee.png",
    "02_T1_Grayscale_Astronaut.png",
    "03_T2_Arithmetic_Dark_Astronaut.png",
    "04_T2_Solarization_Rocket.jpg",
    "05_T2_Channel_Elimination_Blue_Cast.png",
    "06_T3_Histogram_Low_Contrast_Astronaut.png",
    "07_T4_Noise_Reduction_Clean_Coffee.png",
    "08_T4_Sharpening_Cat.png",
    "09_T4_Edge_Detection_Coffee.png",
]


@pytest.fixture
def simple():
    return np.array([[[10, 20, 30], [100, 130, 180]], [[200, 210, 220], [255, 0, 120]]], dtype=np.uint8)


def load(num):
    return decode_image((SAMPLES / FILES[num - 1]).read_bytes())


def test_all_nine_samples_exist_and_decode():
    for filename in FILES:
        f = SAMPLES / filename
        assert f.exists(), filename
        image = decode_image(f.read_bytes())
        assert image.ndim == 3 and image.shape[2] == 3 and image.dtype == np.uint8
        assert image.size


def test_rgb_separation_values(simple):
    result = rgb_channels(simple)
    assert list(result) == ["Red intensity", "Green intensity", "Blue intensity", "Red only", "Green only", "Blue only"]
    assert np.array_equal(result["Red intensity"], simple[:, :, 0])
    assert np.array_equal(result["Green intensity"], simple[:, :, 1])
    assert np.array_equal(result["Blue intensity"], simple[:, :, 2])
    assert np.all(result["Red only"][:, :, 1:] == 0)
    assert np.all(result["Green only"][:, :, [0, 2]] == 0)
    assert np.all(result["Blue only"][:, :, :2] == 0)


def test_grayscale_formula_unchanged(simple):
    r, g, b = cv2.split(simple)
    expected = (0.299*r + 0.587*g + 0.114*b).astype(np.uint8)
    assert np.array_equal(custom_grayscale(simple), expected)


def test_arithmetic_four_operations(simple):
    results = arithmetic(simple, 40, 1.3)
    assert len(results) == 4
    assert np.array_equal(results["Addition (+)"], cv2.add(simple, np.full_like(simple, 40)))
    assert np.array_equal(results["Subtraction (-)"], cv2.subtract(simple, np.full_like(simple, 40)))
    assert np.array_equal(results["Multiplication (*)"], np.clip(simple.astype(float)*1.3,0,255).astype(np.uint8))
    assert np.array_equal(results["Division (/)"], np.clip(simple.astype(float)/1.3,0,255).astype(np.uint8))


def test_negative_and_solarization(simple):
    results = solarization(simple, 128)
    assert np.array_equal(results["Complementary"], 255-simple)
    assert np.array_equal(results["Solarization"], np.where(simple > 128, 255-simple, simple))


def test_channel_elimination(simple):
    results = eliminate_channels(simple)
    assert list(results) == ["Remove Red", "Remove Green", "Remove Blue"]
    for idx, key in enumerate(results):
        assert np.all(results[key][:,:,idx] == 0)
        for other in (0,1,2):
            if other != idx:
                assert np.array_equal(results[key][:,:,other], simple[:,:,other])


def test_histogram_both_algorithms():
    img = load(6)
    results = histogram_enhancement(img, 0)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    assert np.array_equal(results["Grayscale (before)"], gray)
    assert np.array_equal(results["Stretching"], cv2.normalize(gray,None,0,255,cv2.NORM_MINMAX))
    assert np.array_equal(results["Equalization"], cv2.equalizeHist(gray))
    bright = histogram_enhancement(img, 30)
    assert np.mean(bright["Stretching"]) >= np.mean(results["Stretching"])
    dim = histogram_enhancement(img, -30)
    assert np.mean(dim["Stretching"]) <= np.mean(results["Stretching"])


def test_noise_reproducible_and_snr():
    img = load(7)
    a = add_salt_pepper(img, 0.05, 7)
    b = add_salt_pepper(img, 0.05, 7)
    assert np.array_equal(a,b)
    results = denoise(img, 0.05, 3, 7)
    assert np.array_equal(results["Salt & Pepper Noise"], a)
    assert len(results) == 4
    assert snr(img, results["Median Filter"]) > snr(img, a)
    assert recommend_denoise(img,results).operation == "Median Filter"


def test_snr_from_scratch(simple):
    assert snr(simple, simple) == float("inf")
    modified = np.zeros_like(simple)
    expected = 10*np.log10(np.sum(simple.astype(float)**2)/np.sum(simple.astype(float)**2))
    assert snr(simple, modified) == pytest.approx(expected)


def test_sharpening_kernel_matches_notebook(simple):
    img = load(8)
    results = sharpening(img, 7)
    blurred = cv2.GaussianBlur(img, (7,7), 0)
    kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
    assert np.array_equal(results["Gaussian Blur"],blurred)
    assert np.array_equal(results["Custom Sharpening"],cv2.filter2D(blurred,-1,kernel))
    assert recommend_sharpen(img, results).operation in results
    assert psnr(img, img) == float('inf')


def test_edge_detection_exact_notebook_pipeline():
    img = load(9)
    results = edge_detection(img, 50, 150)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    pre = cv2.GaussianBlur(gray,(5,5),0)
    assert np.array_equal(results["Grayscale"],gray)
    assert np.array_equal(results["Gaussian Pre-Blur"],pre)
    assert np.array_equal(results["Canny Edges"],cv2.Canny(pre,50,150))
    assert np.count_nonzero(results["Canny Edges"]) > 0


def test_recommendations_clear_about_limits():
    rgb = load(1)
    assert recommendation_for("RGB Separation",rgb,rgb_channels(rgb)).operation is None
    assert recommendation_for("Edge Detection",rgb,edge_detection(rgb)).operation == "Canny Edges"
    blue = load(5)
    assert recommend_channel(blue).operation == "Remove Blue"
    dark = load(3)
    choice = recommend_arithmetic(dark,arithmetic(dark))
    assert choice.operation is None or choice.operation in arithmetic(dark)
    h = load(6)
    assert recommend_histogram(histogram_enhancement(h)).operation in {None,"Stretching","Equalization"}


def test_decode_round_trip(simple):
    assert np.array_equal(decode_image(encode_png(simple)),simple)
    with pytest.raises(ValueError):
        decode_image(b"not an image")
    with pytest.raises(ValueError):
        decode_image(b"")


def test_input_validation(simple):
    with pytest.raises(ValueError):
        arithmetic(simple, 30, 0)
    with pytest.raises(ValueError):
        solarization(simple, 300)
    with pytest.raises(ValueError):
        denoise(simple, 0.05, 4)
    with pytest.raises(ValueError):
        edge_detection(simple, 150, 50)
    with pytest.raises(ValueError):
        rgb_channels(simple[:,:,0])
