"""Image Processing Lab: pure OpenCV / NumPy operations from the final Colab notebook.

Images are RGB uint8 arrays, grayscale results are 2-D uint8 arrays.
Functions have no Streamlit or file-upload dependency and can be unit-tested.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import cv2
import numpy as np


@dataclass(frozen=True)
class Recommendation:
    """Auditable selection: a goal, a measurement and its scope/limitation."""
    operation: str | None
    reason: str
    basis: str = "rule"
    goal: str = ""
    evidence: tuple[str, ...] = ()
    rows: tuple[dict, ...] = ()
    limitation: str = ""



def validate_rgb(img: np.ndarray) -> np.ndarray:
    if not isinstance(img, np.ndarray) or img.ndim != 3 or img.shape[2] != 3:
        raise ValueError("Expected an RGB image with three channels.")
    if img.dtype != np.uint8 or not img.size:
        raise ValueError("Expected a nonempty uint8 RGB image.")
    return img


def decode_image(binary: bytes, max_pixels: int = 18_000_000) -> np.ndarray:
    """Read PNG/JPG in RGB; avoid excessive sizes and decode failures."""
    if not binary or len(binary) > 20 * 1024 * 1024:
        raise ValueError("Please upload a JPG/PNG image smaller than 20 MB.")
    raw = np.frombuffer(binary, dtype=np.uint8)
    bgr = cv2.imdecode(raw, cv2.IMREAD_COLOR)
    if bgr is None:
        raise ValueError("This file could not be decoded as a valid image.")
    if bgr.shape[0] * bgr.shape[1] > max_pixels:
        raise ValueError("Please use an image smaller than 18 megapixels.")
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def encode_png(img: np.ndarray) -> bytes:
    if img.ndim == 3:
        bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    else:
        bgr = img
    okay, encoded = cv2.imencode(".png", bgr)
    if not okay:
        raise ValueError("Failed to encode image.")
    return encoded.tobytes()


def rgb_channels(img: np.ndarray) -> Dict[str, np.ndarray]:
    r, g, b = cv2.split(validate_rgb(img))
    red = np.zeros_like(img)
    green = np.zeros_like(img)
    blue = np.zeros_like(img)
    red[:, :, 0] = r
    green[:, :, 1] = g
    blue[:, :, 2] = b
    return {
        "Red intensity": r, "Green intensity": g, "Blue intensity": b,
        "Red only": red, "Green only": green, "Blue only": blue,
    }


def custom_grayscale(img: np.ndarray) -> np.ndarray:
    # Preserve the user-approved FINAL notebook formula exactly.
    r, g, b = cv2.split(validate_rgb(img))
    return (0.299 * r + 0.587 * g + 0.114 * b).astype(np.uint8)


def arithmetic(img: np.ndarray, amount: int = 40, factor: float = 1.3) -> Dict[str, np.ndarray]:
    validate_rgb(img)
    if not 0 <= amount <= 255 or factor <= 0:
        raise ValueError("Amount must be 0..255 and factor must be positive.")
    return {
        "Addition (+)": cv2.add(img, np.full_like(img, amount)),
        "Subtraction (-)": cv2.subtract(img, np.full_like(img, amount)),
        "Multiplication (*)": np.clip(img.astype(float) * factor, 0, 255).astype(np.uint8),
        "Division (/)": np.clip(img.astype(float) / factor, 0, 255).astype(np.uint8),
    }


def solarization(img: np.ndarray, threshold: int = 128) -> Dict[str, np.ndarray]:
    validate_rgb(img)
    if not 0 <= threshold <= 255:
        raise ValueError("Threshold must be between 0 and 255.")
    return {
        "Complementary": 255 - img,
        "Solarization": np.where(img > threshold, 255 - img, img).astype(np.uint8),
    }


def eliminate_channels(img: np.ndarray) -> Dict[str, np.ndarray]:
    validate_rgb(img)
    outputs = {}
    for label, channel in (("Remove Red", 0), ("Remove Green", 1), ("Remove Blue", 2)):
        result = img.copy()
        result[:, :, channel] = 0
        outputs[label] = result
    return outputs


def histogram_enhancement(img: np.ndarray, brightness: int = 0) -> Dict[str, np.ndarray]:
    validate_rgb(img)
    if not -255 <= brightness <= 255:
        raise ValueError("Brightness offset must be in the range -255..255.")
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    stretch = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
    eq = cv2.equalizeHist(gray)
    if brightness > 0:
        stretch = cv2.add(stretch, np.full_like(stretch, brightness))
        eq = cv2.add(eq, np.full_like(eq, brightness))
    elif brightness < 0:
        stretch = cv2.subtract(stretch, np.full_like(stretch, -brightness))
        eq = cv2.subtract(eq, np.full_like(eq, -brightness))
    return {"Grayscale (before)": gray, "Stretching": stretch, "Equalization": eq}


def add_salt_pepper(img: np.ndarray, density: float = 0.05, seed: int = 7) -> np.ndarray:
    validate_rgb(img)
    if not 0 <= density <= 1:
        raise ValueError("Noise density must be between 0 and 1.")
    rng = np.random.RandomState(seed)  # Same deterministic generation method as notebook.
    random_pixels = rng.rand(*img.shape[:2])
    out = img.copy()
    out[random_pixels < density / 2] = 0
    out[random_pixels > 1 - density / 2] = 255
    return out


def denoise(img: np.ndarray, density: float = 0.05, kernel: int = 3, seed: int = 7) -> Dict[str, np.ndarray]:
    validate_rgb(img)
    if kernel < 3 or kernel % 2 != 1:
        raise ValueError("Filter kernel must be an odd integer >= 3.")
    noisy = add_salt_pepper(img, density=density, seed=seed)
    return {
        "Salt & Pepper Noise": noisy,
        "Average Filter": cv2.blur(noisy, (kernel, kernel)),
        "Gaussian Filter": cv2.GaussianBlur(noisy, (kernel, kernel), 0),
        "Median Filter": cv2.medianBlur(noisy, kernel),
    }


def snr(original: np.ndarray, changed: np.ndarray) -> float:
    if original.shape != changed.shape:
        raise ValueError("The two images must have the same shape.")
    a, b = original.astype(float), changed.astype(float)
    signal_power = np.sum(a ** 2)
    error_power = np.sum((a - b) ** 2)
    return float("inf") if error_power == 0 else float(10 * np.log10(signal_power / error_power))


def psnr(original: np.ndarray, changed: np.ndarray) -> float:
    if original.shape != changed.shape:
        raise ValueError("The two images must have the same shape.")
    mse = float(np.mean((original.astype(float) - changed.astype(float)) ** 2))
    return float("inf") if mse == 0 else float(10 * np.log10(255 ** 2 / mse))


def sharpening(img: np.ndarray, blur_kernel: int = 7) -> Dict[str, np.ndarray]:
    validate_rgb(img)
    if blur_kernel < 3 or blur_kernel % 2 != 1:
        raise ValueError("Blur kernel must be odd and >= 3.")
    blurred = cv2.GaussianBlur(img, (blur_kernel, blur_kernel), 0)
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(blurred, -1, kernel)
    return {"Gaussian Blur": blurred, "Custom Sharpening": sharpened}


def edge_detection(img: np.ndarray, low: int = 50, high: int = 150) -> Dict[str, np.ndarray]:
    validate_rgb(img)
    if not (0 <= low < high <= 255):
        raise ValueError("Canny thresholds must satisfy 0 <= low < high <= 255.")
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, low, high)
    return {"Grayscale": gray, "Gaussian Pre-Blur": blurred, "Canny Edges": edges}


def brightness_stats(img: np.ndarray) -> dict[str, float]:
    """Descriptive brightness/contrast and clipping, not a perceptual quality score."""
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) if img.ndim == 3 else img
    return {
        "mean": float(np.mean(gray)),
        "contrast": float(np.std(gray)),
        "black_pct": float(np.mean(gray <= 3) * 100),
        "white_pct": float(np.mean(gray >= 252) * 100),
    }


def _gray(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) if img.ndim == 3 else img


def _quantile(img: np.ndarray, value: int) -> float:
    return float(np.percentile(_gray(img), value))


def _new_saturation(original: np.ndarray, result: np.ndarray) -> float:
    """Additional fully dark or any saturated channel pixels (percentage points)."""
    def count(im: np.ndarray) -> float:
        rgb = im if im.ndim == 3 else im[..., None]
        return float(np.mean(np.any(rgb >= 254, axis=2) | np.all(rgb <= 1, axis=2)) * 100)
    return max(0.0, count(result) - count(original))


def recommend_arithmetic(original: np.ndarray, outputs: Dict[str, np.ndarray], goal: str = "Auto") -> Recommendation:
    """Pick for a declared exposure goal; never infer photographic quality from mean=128.

    Candidate ranks are fully reproducible, with clipping + contrast penalties.
    """
    median0 = _quantile(original, 50)
    contrast0 = brightness_stats(original)["contrast"]
    if float(np.percentile(_gray(original), 95) - np.percentile(_gray(original), 5)) < 8:
        return Recommendation(None, "The input is almost uniformly bright or dark (P95 − P5 < 8); shifting the same values cannot recover missing structure.",
                              "grayscale robust intensity range", goal="Avoid false detail recovery claims",
                              evidence=(f"Original P95 − P5: {_quantile(original, 95)-_quantile(original, 5):.1f}",),
                              limitation="An arithmetic operation cannot reconstruct information missing in a flat image.")
    selected_goal = goal
    if goal == "Auto":
        selected_goal = "Brighten" if median0 < 90 else "Darken" if median0 > 175 else "Keep original"
    if selected_goal == "Keep original":
        return Recommendation(None, f"Input median is {median0:.1f}/255; no strong under/overexposure was detected by the declared midtone rule (below 90: brighten; above 175: darken).", "exposure goal rule", goal="Avoid unnecessary changes", evidence=(f"Original median brightness: {median0:.1f}/255",), limitation="Exposure can be artistic or localized; midtones alone cannot certify quality.")
    brighten = selected_goal == "Brighten"
    eligible = ("Addition (+)", "Multiplication (*)") if brighten else ("Subtraction (-)", "Division (/)")
    target = 115 if brighten else 145
    rows = []
    for name, candidate in outputs.items():
        median = _quantile(candidate, 50)
        stats = brightness_stats(candidate)
        delta = _new_saturation(original, candidate)
        contrast_loss = max(0.0, contrast0 - stats["contrast"])
        # Explicit *teaching heuristic*. No-reference image quality has no guaranteed winner.
        score = abs(median - target) + 2.5 * delta + 0.6 * contrast_loss
        rows.append({"Operation": name, "Median": round(median, 1),
                     "New saturation (%)": round(delta, 2),
                     "Contrast loss": round(contrast_loss, 1),
                     "Score (lower is better)": round(score, 2),
                     "Eligible": "Yes" if name in eligible else "No"})
    scores = {row["Operation"]: row["Score (lower is better)"] for row in rows}
    winner = min(eligible, key=scores.get)
    best = next(row for row in rows if row["Operation"] == winner)
    return Recommendation(winner,
        f"For the {selected_goal.lower()} goal, {winner} has the lowest stated score ({scores[winner]:.2f}) among the two operations that move brightness in the required direction.",
        "score = |result median − target| + 2.5 × newly saturated pixels (%) + 0.6 × contrast loss",
        goal=f"{selected_goal} an image · target median {target}/255",
        evidence=(f"Original median {median0:.1f} → result median {best['Median']:.1f} /255",
                  f"Newly saturated pixels: {best['New saturation (%)']:.2f}% · contrast loss: {best['Contrast loss']:.1f}"),
        rows=tuple(rows),
        limitation="This is a declared exposure-preservation heuristic, not an objective photographic quality score. A clipped/dark input cannot regain details lost before processing.")


def recommend_solarization(original: np.ndarray, threshold: int = 128, goal: str = "Selective highlight inversion") -> Recommendation:
    changed = float(np.mean(original > threshold) * 100)
    if goal == "Full color inversion":
        return Recommendation("Complementary", "Complementary computes 255 − pixel on every channel and therefore matches the full-inversion goal exactly.",
                              "operation matches the chosen visual effect", goal=goal,
                              evidence=("All color channels are inverted throughout the image.",),
                              limitation="This is a visual-effect choice, not a scientific image-quality ranking.")
    if changed < 1 or changed > 85:
        return Recommendation(None, f"Solarization would invert {changed:.1f}% of channel values at threshold {threshold}, so the selective effect is too weak or too close to full inversion for a clear automatic recommendation.",
                              "changed channel fraction", goal=goal,
                              evidence=(f"Channels over threshold: {changed:.1f}%",),
                              limitation="Visual preference cannot be inferred from pixels alone.")
    return Recommendation("Solarization",
        f"Solarization inverts the {changed:.1f}% of channel values above {threshold} while preserving the remaining {100-changed:.1f}%. Complementary would invert the entire image.",
        "effect coverage; desired operation defined by the user", goal=goal,
        evidence=(f"Threshold {threshold}/255", f"Changed {changed:.1f}% · unchanged {100-changed:.1f}% of channel values"),
        limitation="Best match for the selected effect only; not a proof of visual superiority.")


def recommend_channel(original: np.ndarray) -> Recommendation:
    avg = original.mean(axis=(0, 1))
    order = np.argsort(avg)
    high, second = int(order[-1]), int(order[-2])
    names = ("Red", "Green", "Blue")
    gap = float(avg[high] - avg[second])
    rows = tuple({"Channel": name, "Mean intensity": round(float(avg[i]), 2),
                  "Remove option": f"Remove {name}"} for i, name in enumerate(names))
    if gap < 25:
        return Recommendation(None, "The strongest channel is less than 25 intensity units above the second strongest; there is no substantial global dominance to diagnose.",
                              "RGB mean gap", goal="Demonstrate removal of a strongly dominant channel", rows=rows,
                              evidence=(f"Largest mean gap: {gap:.1f}/255",),
                              limitation="A colorful subject can have naturally unequal channel means. Channel removal cannot reliably correct color casts.")
    return Recommendation(f"Remove {names[high]}",
        f"The {names[high]} channel has the highest image-wide mean ({avg[high]:.1f}), {gap:.1f} levels above {names[second]} ({avg[second]:.1f}). Under the specified channel-dominance task, this is the strongest candidate to demonstrate removal.",
        "channel mean and runner-up gap (minimum diagnostic gap 25)",
        goal="Eliminate one dominant RGB channel for visual analysis",
        rows=rows, evidence=(f"Mean R/G/B: {avg[0]:.1f} / {avg[1]:.1f} / {avg[2]:.1f}", f"Leading-channel margin: {gap:.1f}"),
        limitation="A dominant channel is not proof of an unwanted color cast; removing it discards information and often creates an unnatural tint. Check the scene and RGB matrix.")


def recommend_histogram(outputs: Dict[str, np.ndarray]) -> Recommendation:
    """Assess stretching vs equalization for low-contrast images.

    Use measured gain and endpoint occupancy; avoid maximizing contrast alone.
    """
    before = outputs["Grayscale (before)"]
    src = brightness_stats(before)
    rows = []
    for name in ("Stretching", "Equalization"):
        stat = brightness_stats(outputs[name])
        clipped = stat["black_pct"] + stat["white_pct"]
        gain = stat["contrast"] - src["contrast"]
        rows.append({"Method": name, "Contrast (std)": round(stat["contrast"], 2),
                     "Contrast gain": round(gain, 2), "Near-extreme pixels (%)": round(clipped, 2)})
    evidence = (f"Original contrast (std): {src['contrast']:.1f}",
                "Near-extreme pixels are gray intensities ≤3 or ≥252.")
    if src["contrast"] >= 50:
        return Recommendation(None, "The image already has a wide intensity distribution (std ≥50); automatic enhancement isn't justified by low-contrast evidence.",
                              "pre-enhancement grayscale std", goal="Improve low contrast while limiting extreme intensities",
                              evidence=evidence, rows=tuple(rows),
                              limitation="Contrast standard deviation is not a perceptual quality score.")
    qualified = [r for r in rows if r["Contrast gain"] >= 10]
    if not qualified:
        return Recommendation(None, "Neither method increases intensity contrast by at least 10 standard-deviation units.",
                              "contrast gain gate", goal="Improve low contrast while limiting extreme intensities",
                              evidence=evidence, rows=tuple(rows))
    # First avoid accumulating extremely dark/bright values; then prefer greater gain.
    winner = min(qualified, key=lambda r: (r["Near-extreme pixels (%)"], -r["Contrast gain"]))
    clip = winner["Near-extreme pixels (%)"]
    return Recommendation(winner["Method"],
        f"Both methods were evaluated on the same grayscale input. {winner['Method']} adds {winner['Contrast gain']:.1f} std units, with {clip:.1f}% of pixels near black/white; among qualifying results it has the lowest extreme-pixel rate.",
        "contrast gain ≥10; then minimize near-extreme pixels (tie: higher gain)",
        goal="Restore spread in a low-contrast image with fewer extreme pixels",
        evidence=evidence + (f"Selected: {winner['Contrast (std)']:.1f} std; {clip:.1f}% near extremes.",),
        rows=tuple(rows),
        limitation="Contrast and clipping are proxy measures; they cannot prove the most natural-looking output. Strong enhancement can amplify noise, and brightness offset changes the comparison.")


def recommend_denoise(original: np.ndarray, outputs: Dict[str, np.ndarray]) -> Recommendation:
    noise = snr(original, outputs["Salt & Pepper Noise"])
    rows = []
    if np.isposinf(noise):
        return Recommendation(None, "The noisy stage is identical to the clean image (infinite SNR); smoothing is unnecessary and may blur details.",
                              "SNR against clean original", goal="Recover the clean image after simulated noise",
                              evidence=("No degradation to recover from this noise setting.",),
                              limitation="For a real noisy photo without a clean original, reference SNR is unavailable.")
    for name in ("Average Filter", "Gaussian Filter", "Median Filter"):
        score = snr(original, outputs[name])
        rows.append({"Method": name, "SNR (dB)": round(score, 3),
                     "Gain vs noisy (dB)": round(score - noise, 3)})
    best = max(rows, key=lambda r: r["SNR (dB)"])
    if best["SNR (dB)"] <= noise + 0.05:
        return Recommendation(None, "No smoothing filter improved measured SNR over the noisy input.",
                              "SNR against clean original", goal="Recover the clean input after injected noise",
                              rows=tuple(rows), evidence=(f"Noisy SNR: {noise:.2f} dB",))
    return Recommendation(best["Method"],
        f"{best['Method']} has the highest measured SNR ({best['SNR (dB)']:.2f} dB) against the original clean image, improving by {best['Gain vs noisy (dB)']:.2f} dB over the noisy image.",
        "SNR = 10 × log10(Σ original² / Σ(original − result)²)",
        goal="Recover the clean image after simulated salt-and-pepper noise",
        evidence=(f"Noisy input SNR: {noise:.2f} dB", f"Highest filter SNR: {best['SNR (dB)']:.2f} dB"),
        rows=tuple(rows), limitation="This comparison is valid here because the app has the original clean image before adding noise. Uploaded real noisy images without a clean reference need another evaluation method.")


def recommend_sharpen(original: np.ndarray, outputs: Dict[str, np.ndarray]) -> Recommendation:
    blurred = psnr(original, outputs["Gaussian Blur"])
    sharp = psnr(original, outputs["Custom Sharpening"])
    rows = ({"Result": "Gaussian Blur", "PSNR (dB)": round(blurred, 3)},
            {"Result": "Custom Sharpening", "PSNR (dB)": round(sharp, 3)})
    gain = sharp - blurred
    if np.isposinf(blurred):
        return Recommendation(None, "The Gaussian-blurred stage is identical to the clean input (PSNR is infinite), so there is no reconstruction improvement to measure.",
                              "PSNR against clean original", goal="Recover the clean reference after simulated blur",
                              evidence=("Blurred image already matches the clean original.",), rows=rows,
                              limitation="Uniform or blur-invariant images cannot establish a sharpening benefit.")
    if gain <= 0.1:
        return Recommendation(None, f"Sharpening did not reliably improve fidelity: PSNR gain is {gain:.2f} dB (minimum required: >0.10 dB).",
                              "PSNR against original clean image", goal="Recover the clean reference after induced blur",
                              evidence=(f"Blurred PSNR: {blurred:.2f} dB", f"Sharpened PSNR: {sharp:.2f} dB"), rows=rows,
                              limitation="PSNR assesses fidelity, not perceived sharpness or artistic enhancement.")
    return Recommendation("Custom Sharpening", f"Custom Sharpening restores more of the original signal after simulated blur: PSNR improves from {blurred:.2f} to {sharp:.2f} dB (+{gain:.2f} dB).",
                          "PSNR = 10 × log10(255² / MSE) against the original clean image",
                          goal="Recover the original clean image after applied Gaussian blur",
                          evidence=(f"PSNR gain vs Gaussian Blur: +{gain:.2f} dB",), rows=rows,
                          limitation="This demonstrates improved similarity to the known clean reference, not universal perceptual sharpness.")


def recommendation_for(module: str, original: np.ndarray, outputs: Dict[str, np.ndarray], **params) -> Recommendation:
    if module == "Arithmetic":
        return recommend_arithmetic(original, outputs, str(params.get("exposure_goal", "Auto")))
    if module == "Complementary / Solarization":
        return recommend_solarization(original, int(params.get("threshold", 128)), str(params.get("effect_goal", "Selective highlight inversion")))
    if module == "Channel Elimination":
        return recommend_channel(original)
    if module == "Histogram Enhancement":
        return recommend_histogram(outputs)
    if module == "Noise Reduction":
        return recommend_denoise(original, outputs)
    if module == "Sharpening":
        return recommend_sharpen(original, outputs)
    if module == "RGB Separation":
        return Recommendation(None, "Each RGB view isolates different information; there is no defensible quality ranking between channels.",
                              "non-comparable channel representations", goal="Inspect color-channel information", limitation="Choose a channel according to the feature you want to inspect.")
    if module == "Custom Grayscale":
        return Recommendation("Custom Grayscale", "This is the only grayscale conversion implemented, using the exact formula approved in the notebook.",
                              "single implemented transformation", goal="Convert RGB to grayscale with weighted channels")
    if module == "Edge Detection":
        return Recommendation("Canny Edges", "Canny is the only edge detector implemented in the approved notebook; grayscale and Gaussian blur are preparation steps, not competing detectors.",
                              "single studied operator in the app", goal="Outline structural boundaries",
                              limitation="No benchmark against Sobel, Prewitt, or a labeled edge map is claimed.")
    raise ValueError(f"Unknown module: {module}")
