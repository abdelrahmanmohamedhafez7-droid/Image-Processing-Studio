<div align="center">

# Image Processing Studio

**An interactive digital image processing lab built with Python, OpenCV, NumPy, and Streamlit.**

Explore individual algorithms, compare their outputs, inspect image metrics, and understand why a particular result may be recommended.

[![Live App](https://img.shields.io/badge/Live%20Demo-Open%20Streamlit%20App-FF4B4B?logo=streamlit&logoColor=white)](https://image-processing-studio-01.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11%20recommended-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Image%20Processing-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Interactive%20Dashboard-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)

**[Launch the live app](https://image-processing-studio-01.streamlit.app/)** · **[Browse the source code](Image_Processing_Streamlit_Studio_COMPLETE/Image_Processing_Streamlit_Studio/)** · **[Open the notebook](Image_Processing_Colab_VSCode_FINAL_REDOWNLOAD.ipynb)**

</div>

---

## Overview

Image Processing Studio combines **four course sections** and **nine practical image-processing modules** into one dashboard. The core algorithms are based on a companion Jupyter notebook and implemented with straightforward OpenCV and NumPy functions.

The dashboard supports both **dark and light themes**, image upload, ready-to-use sample images, adjustable parameters, individual algorithm previews, side-by-side comparisons, and PNG/ZIP exports.

The **original image stays visible** while you explore the processing results. Choose an algorithm to see its output alone, or select **Compare All** to inspect the results together and view a measurement-based recommendation where one can reasonably be made.

## Processing modules

| Section | Module | Available results |
|---|---|---|
| **Color Fundamentals** | RGB Separation | Red, green, and blue intensity maps; isolated R/G/B color channels |
| | Weighted Grayscale | Grayscale conversion using `0.299R + 0.587G + 0.114B` |
| **Point Operations** | Arithmetic | Addition (+), subtraction (−), multiplication (×), division (÷) |
| | Complementary / Solarization | Full negative; threshold-based selective inversion |
| | Channel Elimination | Remove red, green, or blue; inspect RGB channel statistics |
| **Contrast & Histogram** | Histogram Enhancement | Original grayscale histogram; contrast stretching; histogram equalization; brightness adjustment |
| **Filters & Edges** | Noise Reduction | Injected salt-and-pepper noise; average, Gaussian, and median filters; SNR |
| | Sharpening | Gaussian-blurred image; custom-kernel sharpening; PSNR |
| | Edge Detection | Grayscale; Gaussian pre-blur; Canny edge detection |

> **Note:** Grayscale, Gaussian pre-blur, and Canny are separate processing *stages* in the edge-detection demonstration, not three competing edge detectors. The grayscale equation above is the notebook's standard weighted conversion formula.

## How the dashboard works

1. **Choose a section and module** from the navigation.
2. **Upload a JPG/PNG image**, or select the sample prepared for that module.
3. **Adjust parameters**, such as arithmetic amount, solarization threshold, filter kernel size, or Canny thresholds.
4. **Select one algorithm** to view that processed output beside the always-visible original.
5. **Choose Compare All** to inspect every applicable result, measured values, and a recommendation or an explicit statement that no reliable automatic winner exists.
6. **Download** the selected processed image as PNG or all comparison results as ZIP.

## What “Best” means here

The dashboard makes **goal-specific, explainable recommendations**, not claims about a universally best-looking photograph. Each recommendation explains the chosen goal, decision rule, evidence, and limitations.

| Module | Decision basis |
|---|---|
| Arithmetic | Declared brightening/darkening goal, output median intensity, newly saturated pixels, and contrast loss; a transparent *heuristic* |
| Complementary / Solarization | Which operation matches the selected artistic effect; **no universal image-quality winner** |
| Channel Elimination | A substantial difference between average RGB channel intensities; **diagnostic demonstration**, not a validated color-correction method |
| Histogram Enhancement | Measured contrast improvement balanced against near-black and near-white pixel percentages |
| Noise Reduction | Highest **SNR**, measured against the known clean image before synthetic noise is added |
| Sharpening | **PSNR** improvement relative to the known clean image before simulated blur |
| RGB / Grayscale / Edge Detection | No forced comparison when outputs represent different information, a single formula, or sequential processing stages |

For decision rules, formulas, example values, and caveats, see **[Recommendation Methods](Image_Processing_Streamlit_Studio_COMPLETE/Image_Processing_Streamlit_Studio/RECOMMENDATION_METHODS.md)**.

### SNR and PSNR

Noise reduction uses a reference-based signal-to-noise ratio calculated directly from pixel values:

```text
SNR (dB) = 10 log10 [ Σ(original²) / Σ((original − result)²) ]
```

Sharpening uses peak signal-to-noise ratio against the clean source:

```text
MSE       = mean((original − result)²)
PSNR (dB) = 10 log10 (255² / MSE)
```

These metrics are meaningful in this project because the clean reference exists **before the application adds noise or blur**. They should not be presented as measured ground-truth quality for an arbitrary already-damaged upload.

## Repository structure

```text
Image-Processing-Studio/
├── README.md                               # This project overview
├── REQ.TXT                                 # Notebook/VS Code dependencies
├── Image_Processing_Colab_VSCode_FINAL_REDOWNLOAD.ipynb
├── Image_Processing_4_Tasks_Image_Pack/    # Nine original demonstration inputs
├── .gitignore
└── Image_Processing_Streamlit_Studio_COMPLETE/
    └── Image_Processing_Streamlit_Studio/
        ├── app.py                         # Streamlit UI and interactions
        ├── processing.py                  # Image-processing logic and selection rules
        ├── ui_style.py                    # Coordinated dark/light theme
        ├── RECOMMENDATION_METHODS.md      # Explanation of the recommendations
        ├── requirements.txt               # Web app dependencies
        ├── RUN_WINDOWS.bat                # Windows local launcher
        ├── .streamlit/config.toml
        ├── assets/samples/                # In-app demo images
        └── tests/                         # Processing and UI-smoke tests
```

The image pack and the app's `assets/samples/` directory intentionally contain the same nine demo images. The top-level image pack is for standalone notebook/lab use; the nested copies are used by the hosted app.

## Run the Streamlit app locally (Windows CMD)

Install [Python](https://www.python.org/downloads/) (Python 3.11 recommended), then run these commands in **Windows CMD**:

```bat
git clone https://github.com/abdelrahmanmohamedhafez7-droid/Image-Processing-Studio.git
cd Image-Processing-Studio
cd Image_Processing_Streamlit_Studio_COMPLETE\Image_Processing_Streamlit_Studio

py -3.11 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If you already have the repository locally, open CMD in its root folder and skip the `git clone` step. Alternatively, run `RUN_WINDOWS.bat` from the app folder. Open `http://localhost:8501` if the browser does not launch automatically.

## Run the notebook in VS Code

The companion notebook is compatible with Google Colab and local Jupyter/VS Code usage. On Windows, from the **repository root**:

```bat
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r REQ.TXT
```

Open `Image_Processing_Colab_VSCode_FINAL_REDOWNLOAD.ipynb` in VS Code, install the **Python** and **Jupyter** extensions, and select the `.venv` kernel. Image upload uses the Colab uploader on Colab and a local file picker in compatible desktop environments. Run cells again if you want to process different images.

## Tests

From the **Streamlit app folder**:

```bat
python -m pip install pytest
python -m pytest -q
```

The project includes tests for image processing, recommendation edge cases, and simulated Streamlit UI paths. Automated tests do not replace a manual browser check of the deployed interface and both color themes.

## Deployment

This project is hosted on **Streamlit Community Cloud**:

- **Live URL:** https://image-processing-studio-01.streamlit.app/
- **Repository:** https://github.com/abdelrahmanmohamedhafez7-droid/Image-Processing-Studio
- **Branch:** `main`
- **Entrypoint:** `Image_Processing_Streamlit_Studio_COMPLETE/Image_Processing_Streamlit_Studio/app.py`
- **Web dependencies:** `Image_Processing_Streamlit_Studio_COMPLETE/Image_Processing_Streamlit_Studio/requirements.txt`

The notebook uses the separate top-level `REQ.TXT` dependency list. No API keys are required for the image-processing dashboard.

## Sample images

The nine demo images are provided in `Image_Processing_4_Tasks_Image_Pack/`, with a README explaining their intended tasks. They include color-rich images, deliberately darkened or low-contrast images, a simulated blue color cast, and clean references for adding noise or blur. Source imagery is based on standard `scikit-image` / `imageio` samples (Coffee, Astronaut, Cat, Rocket).

## Scope and limitations

- The app is a **teaching and experimentation tool**, not a professional photographic quality assessor.
- A result described as *recommended* is selected **under the stated rule and goal**. For some operations no meaningful automatic winner exists.
- The weighted grayscale formula is the one retained in the coursework notebook; it is not a novel formula.
- Different user-provided images or parameter values can produce different recommendation outcomes.
- Canny is the only implemented edge detector; additional algorithms are outside the current coursework scope.

---

<div align="center">

**Built for hands-on image-processing practice and clear, inspectable visual comparisons.**

[Open the dashboard](https://image-processing-studio-01.streamlit.app/) · [Read the recommendation methodology](Image_Processing_Streamlit_Studio_COMPLETE/Image_Processing_Streamlit_Studio/RECOMMENDATION_METHODS.md)

</div>
