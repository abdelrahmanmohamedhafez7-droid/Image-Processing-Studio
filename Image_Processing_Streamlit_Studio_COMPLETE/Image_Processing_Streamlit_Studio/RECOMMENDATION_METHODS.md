# Recommendation logic · Explainable selection for the lab

## The rule used in the app

A label such as **Recommended** means **the best candidate under a stated goal and measurable comparison**. It does **not** mean a universally “perfect image”. In the app's Compare All mode, you can always find: (1) the desired goal, (2) an operation, if justified, (3) the precise decision rule, (4) the measured candidate table where applicable, and (5) a limitation.

### Arithmetic (addition, subtraction, multiplication, division)

**Question:** Is the goal to make a dark photo brighter, or to make a bright photo darker?

- With `Auto`, median grayscale below 90/255 suggests **Brighten**; above 175 suggests **Darken**; otherwise **No automatic change**. This is a simple teaching definition of under/overexposure. `Auto` can be overridden in the sidebar.
- When brightening, compare **Addition** and **Multiplication**. When darkening, compare **Subtraction** and **Division**. The other two are shown, but marked *not eligible for this goal*.
- Score to minimize:

  `abs(result_median - target) + 2.5 * newly_saturated_percent + 0.6 * contrast_loss`

  The target median is 115 for brightening and 145 for darkening, chosen as practical midtone anchors (not universal photographic optima). `newly_saturated_percent` is the additional percentage of pixels that become wholly black or have at least one nearly saturated 8-bit channel; `contrast_loss` is any reduction in grayscale standard deviation from the original.
- The smallest score is recommended, but the score is a **reference-free exposure heuristic**. Brightening a black region does not reconstruct lost content.
- On the included intentionally dark Astronaut photo, this declared rule recommends **Addition (+40)**. The earlier Colab's human-selected **Multiplication (×1.3)** is still available and unchanged, but visual preference and a measurable heuristic can disagree.

### Complementary vs Solarization

**Question:** What visual effect do you want to demonstrate?

- **Selective highlight inversion:** Solarization flips only values above the threshold. It is suggested when between 1% and 85% of channel values would change. Otherwise there is no defensible automatic suggestion, because the selective effect is absent or too close to full inversion.
- **Full color inversion:** Complementary inverts all channel values (`255 − image`), exactly matching that stated effect.
- There is no scientific image-quality winner between these artistic transformations.

### Channel Elimination

- Measure `mean(R), mean(G), mean(B)`.
- If the highest mean exceeds the second-highest by **at least 25** intensity levels, suggest **removing the strongest** for a channel-dominance demonstration. Show all three means and a first 3×3 RGB matrix.
- The demo blue-cast photo has channel means approximately **R=158.6, G=85.8, B=204.8**; Blue leads Red by **46.3** and is thus the strongest candidate under this *specified diagnostic rule*.
- This is not a validated **color correction** procedure; bright red/orange objects can naturally produce a large red mean. Removing a channel is destructive and can produce an unnatural tint. If no channel dominates sufficiently, the app declines a winner.

### Histogram Stretching vs Equalization

- Start with grayscale. `Contrast` is the standard deviation of intensities.
- If original contrast already meets **50** intensity levels, decline automatic enhancement.
- Require each candidate to improve contrast by at least **10** levels.
- Choose the qualifying candidate with fewer near-extreme pixels (gray values <=3 or >=252), using stronger contrast gain only as a tiebreaker.
- The intentionally low-contrast Astronaut sample has starting contrast **19.45**, Stretching **75.15** with **14.17%** near extremes, and Equalization **81.85** with **14.83%** near extremes. Therefore **Stretching** is selected to minimize extreme occupancy among eligible results.
- These numbers say nothing definitive about perceived beauty or recoverable information; check the visible histograms and noise.

### Noise Reduction

The original uploaded picture is explicitly the **clean reference**, and the app itself injects Salt & Pepper noise, so reference comparison is justified.

`SNR_dB = 10 * log10(Σclean² / Σ(clean − filtered)²)`

The filter with the **highest SNR** that beats the noisy stage wins. Included Coffee test with noise density 5%, kernel 3 and seed 7 gives Median approximately **23.24 dB**; Average **18.34 dB**, Gaussian **18.20 dB**, noisy image **11.36 dB**. If noise density is 0, no filter is needed.

### Sharpening

The app blurs a clean original with Gaussian Blur and then applies the notebook's custom kernel:

```text
 0 -1  0
-1  5 -1
 0 -1  0
```

`PSNR_dB = 10 * log10(255² / mean((clean − reconstructed)²))`

The custom sharpened reconstruction is suggested only when **PSNR exceeds the blurred image PSNR by >0.10 dB**. The demo Cat results are roughly **31.55 dB blurred** and **33.31 dB sharpened**; improving fidelity by ~1.75 dB. This does not prove that every texture looks sharper to the eye.

### RGB / Grayscale / Edge Detection

- RGB separation: Each channel contains different spectral information. **No comparable best**.
- Custom Grayscale: One fixed approved weighted equation, no competition.
- Edge Detection: Grayscale and Gaussian pre-blur are **preprocessing**; **Canny** is the one implemented edge operator. It is labeled as the selected method, not as experimentally superior to unimplemented detectors.

## Practical speaking tip

For every suggestion, explain **what was measured → why it was relevant to the goal → what it does NOT guarantee**. If there is no applicable reference or measurable quality criterion, a responsible answer is that no automatic winner is scientifically established.
