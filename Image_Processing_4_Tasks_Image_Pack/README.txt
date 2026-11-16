IMAGE PROCESSING LAB — COLAB IMAGE PACK
=======================================
Each image is for one code section in the English Colab notebook.

TASK 1
01_T1_RGB_Separation_Coffee.png: Color photo with strong red/brown tones and white highlights.
02_T1_Grayscale_Astronaut.png: Color photo suitable for weighted custom grayscale conversion.

TASK 2
03_T2_Arithmetic_Dark_Astronaut.png: INTENTIONALLY DARKENED image; notebook has operation "+" and amount=40.
04_T2_Solarization_Rocket.jpg: Bright lights against a dark sky for solarization (threshold=128).
05_T2_Channel_Elimination_Blue_Cast.png: INTENTIONALLY MODIFIED blue channel; remove blue in the notebook.
   Note: This eliminates a corrupted channel but does not reconstruct natural full color.

TASK 3
06_T3_Histogram_Low_Contrast_Astronaut.png: INTENTIONALLY CONTRAST-COMPRESSED image;
   grayscale values span only a narrow range; stretching expands the histogram.

TASK 4
07_T4_Noise_Reduction_Clean_Coffee.png: CLEAN image; notebook ADDS salt-and-pepper noise, then median-filters it.
08_T4_Sharpening_Cat.png: CLEAN image with whisker/fur detail; notebook BLURS it then sharpens.
09_T4_Edge_Detection_Coffee.png: Cup, spoon and plate have clear contour boundaries for Canny.

IMPORTANT: The dark, blue-cast and low-contrast images were SIMULATED / MODIFIED
from public reference photos for controlled classroom demonstrations; do not
claim these are genuine defective camera captures.

Original photo sources:
- Coffee: https://raw.githubusercontent.com/imageio/test_images/master/coffee.png
- Astronaut: https://raw.githubusercontent.com/imageio/test_images/master/astronaut.png
- Cat: https://raw.githubusercontent.com/imageio/test_images/master/chelsea.png
- Rocket: https://raw.githubusercontent.com/scikit-image/scikit-image/v0.25.2/skimage/data/rocket.jpg
Reference: https://scikit-image.org/docs/stable/api/skimage.data.html

Open your notebook, run Setup first, then upload corresponding image in each task cell.
