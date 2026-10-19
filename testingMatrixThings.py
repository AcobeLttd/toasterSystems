
#!/usr/bin/env python3

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw

options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 2
options.parallel = 1
options.hardware_mapping = "regular"

matrix = RGBMatrix(options=options)

image = Image.new("RGB", (128, 32))
draw = ImageDraw.Draw(image)

image = Image.new("RGB", (128, 32), (0, 0, 0))
image.paste((255, 0, 0), (0, 0, 64, 32))       # Red half
image.paste((0, 255, 0), (64, 0, 128, 32))     # Green half

matrix.SetImage(image)
input("Press Enter to exit...")
matrix.Clear()
