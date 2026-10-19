
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

image = Image.open("./test-images/blåhaj.png").convert("RGBA")

# Composite transparency onto black at original size
background = Image.new("RGBA", image.size, (0, 0, 0, 255))
image = Image.alpha_composite(background, image).convert("RGB")

# Show the image at its original size, without resizing
canvas = Image.new("RGB", (128, 32), (0, 0, 0))
canvas.paste(image, (0, 0))



matrix.SetImage(canvas)
input("Press Enter to exit...")
matrix.Clear()
