
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

image = Image.open("./test-images/blåhaj.png").convert("RGB")
image = image.resize((128, 32), Image.Resampling.LANCZOS)


matrix.SetImage(image)
input("Press Enter to exit...")
matrix.Clear()
