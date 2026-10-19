
#!/usr/bin/env python3

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image


options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 2
options.parallel = 1
options.hardware_mapping = "regular"

matrix = RGBMatrix(options=options)

image = Image.open("./test-images/actualPNGtest.png").convert("RGBA")
# Fit the image to one panel
image.thumbnail((64, 32), Image.Resampling.LANCZOS)

# Center it on a transparent-sized black panel
panel = Image.new("RGBA", (64, 32), (0, 0, 0, 255))
x = (64 - image.width) // 2
y = (32 - image.height) // 2
panel.alpha_composite(image, (x, y))

# Convert to RGB and duplicate, mirroring the second panel
panel = panel.convert("RGB")
canvas = Image.new("RGB", (128, 32), (0, 0, 0))
canvas.paste(panel, (0, 0))
canvas.paste(panel.transpose(Image.Transpose.FLIP_LEFT_RIGHT), (64, 0))


matrix.SetImage(canvas)
input("Press Enter to exit...")
matrix.Clear()
