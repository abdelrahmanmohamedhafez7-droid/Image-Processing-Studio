# Image Processing Studio · V2

A polished **Streamlit dashboard** for the nine practical parts in the final executed Image Processing Colab notebook. Every algorithm remains a small, separate OpenCV/NumPy function. The app adds interactive comparison and *explainable, goal-specific* suggestions.

## Run on Windows

1. Install Python 3.10 or newer.
2. Extract this folder.
3. Double-click `RUN_WINDOWS.bat` (internet required the first time).
4. Open **http://localhost:8501** if the browser did not open automatically.

Or use the terminal inside this folder:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The Colab notebook is still a separate, runnable artifact. The Streamlit app does not need a Colab runtime.

## The user interface

The four categories are shown **in the original order** without numbered “Task 1/2/3/4” headings:

1. Color Fundamentals
2. Point Operations
3. Contrast & Histogram
4. Filters & Edges

Within each category, choose one technique using the sidebar. Upload one image (shared across the app) or choose one of the nine included demo inputs. The **original is always visible**.

For each technique, **one individual button = only that result next to the original**. The last wide button, **Compare all · Recommendation**, displays every output and the corresponding explanation and measurements. The theme switch is a **sun/moon icon**, with a shared dark or light palette throughout the dashboard. Download either an individual PNG or every result in a ZIP.

| Category | Technique | Individual outputs |
| --- | --- | --- |
| Color Fundamentals | RGB Separation | R/G/B intensities, R/G/B isolated colors |
| Color Fundamentals | Custom Grayscale | Weighted RGB grayscale |
| Point Operations | Arithmetic | Addition, Subtraction, Multiplication, Division |
| Point Operations | Complementary / Solarization | Complementary, Solarization |
| Point Operations | Channel Elimination | Remove Red, Remove Green, Remove Blue |
| Contrast & Histogram | Histogram Enhancement | Grayscale before, Stretching, Equalization |
| Filters & Edges | Noise Reduction | Salt & Pepper, Average, Gaussian, Median |
| Filters & Edges | Sharpening | Gaussian Blur, Custom Sharpening |
| Filters & Edges | Edge Detection | Grayscale, Gaussian pre-blur, Canny Edges |

## Why a result is suggested

**Important:** “Recommended” means **best under the displayed and reproducible goal/rule**, *not* guaranteed most attractive to the human eye. A reliable absolute best often does not exist for an arbitrary uploaded picture. The app says *No defensible automatic winner* when the condition is not supported. Open the comparison panel to see the actual numbers, rule, and limitations. See [`RECOMMENDATION_METHODS.md`](RECOMMENDATION_METHODS.md) for the full explanation you can use in a lab discussion.

- **Arithmetic:** Auto selects *Brighten* if original grayscale median is under 90, *Darken* if it is over 175, and otherwise leaves the image unchanged. You can override the goal. The app ranks only the operations in the direction of the chosen goal, by absolute distance from the declared midtone target, added saturation, and lost contrast. It shows each term and the score. This is an educational heuristic, not an objective general photo-quality metric.
- **Complementary / Solarization:** The user picks the desired effect: selective highlight inversion or full negative. A method is recommended only as a match to that **explicit artistic goal**. Too few/too many inverted values can produce no automatic winner.
- **Channel Elimination:** A global RGB mean dominance diagnostic ranks the channel that exceeds the runner-up by at least 25 intensity units. Removing it demonstrates the effect; it does **not** prove the photo has a color cast or that deleting the channel corrects it.
- **Histogram:** If the original grayscale contrast (standard deviation) is already at least 50, the app does not demand enhancement. Otherwise a candidate must gain at least 10 units of contrast, and the app selects the one with *fewer near-black/near-white pixels*; contrast gain breaks a tie. These are inspectable proxies, not perceptual truth.
- **Noise Reduction:** Filters are evaluated using **SNR from scratch relative to the known clean image** (before the app injects Salt & Pepper noise). The filter with the highest SNR wins if it improves on the noisy image. If no noise is injected, there is no useful winner.
- **Sharpening:** A clean uploaded image is first blurred; the custom kernel processes the blurred result. The winner is the custom sharpened output **only if its PSNR against the known clean original beats Gaussian Blur by more than 0.1 dB**. Otherwise no claim of restoration is made.
- **RGB:** No scientifically meaningful best between color-channel views.
- **Grayscale:** One approved weighted formula, not a competition.
- **Edge Detection:** Canny is the only edge detection operator; grayscale and Gaussian blur are preprocessing stages, not rival edge detectors.

### Exact notebook fidelity

The nine core processing algorithms match the notebook's tested operations: `cv2.split`, the fixed `0.299 R + 0.587 G + 0.114 B` grayscale formula, OpenCV saturating addition/subtraction, NumPy multiplication/division, complementary, threshold solarization, elimination of one channel, `cv2.normalize`, `cv2.equalizeHist`, deterministic salt-and-pepper noise, Average/Gaussian/Median, SNR from scratch, Gaussian blur with the `[[0,-1,0],[-1,5,-1],[0,-1,0]]` sharpening kernel, and Gaussian + Canny.

The app intentionally adds **UI features** not found in the baseline Colab, such as sliders, alternative channel-removal buttons, testable comparison criteria, and before/after metrics. It does not claim these additional interfaces were previously run in Colab.

## Deploy to Streamlit Community Cloud

1. Upload the **extracted folder contents** to GitHub, keeping `assets/samples/` and `.streamlit/config.toml`.
2. Visit https://share.streamlit.io and choose **Create app**.
3. Point to your repository/branch with entrypoint `app.py`.
4. Deploy; no API key or secret is required.

## Files

```text
Image_Processing_Streamlit_Studio/
├── app.py                       Streamlit navigation and live results
├── processing.py                Original algorithms + auditable selection logic
├── ui_style.py                  Coordinated light/dark CSS palette
├── RECOMMENDATION_METHODS.md    How/why each recommendation is made
├── assets/samples/              Nine original classroom demo inputs
├── tests/test_processing.py     Baseline regression tests
├── tests/test_recommendations_v2.py  Recommendation edge-case tests
├── tests/test_app_smoke.py      All modules in both palettes (simulated UI)
├── requirements.txt
├── .streamlit/config.toml
├── RUN_WINDOWS.bat
└── README.md
```

Run all automated tests:

```bash
python -m pip install pytest
python -m pytest -q
```

### Validation limitation

Processing functions and simulated Streamlit render paths were tested in an offline environment. **No real browser visual test was possible there**, because the Streamlit package could not be installed from the isolated environment. Run the Windows launcher and inspect the actual dashboard, especially both theme modes, before demonstrating the final UI.

### Demo image provenance

The demonstration images are from the companion image pack. The dark, low-contrast and blue-cast pictures are deliberately altered teaching examples. Their source photos are standard `scikit-image`/`imageio` examples (Coffee, Astronaut, Cat, Rocket).
