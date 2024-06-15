from skimage import color
import numpy as np

RGB = [0, 1.0, 1.0]

Lab = color.rgb2lab(RGB)
print(Lab)
