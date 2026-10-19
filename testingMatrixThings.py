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

draw.rectangle((0, 0, 63, 31), fill=(0, 0, 0))
draw.rectangle((0, 0, 31, 31), fill=(255, 0, 0))
draw.rectangle((32, 0, 63, 31), fill=(0, 255, 0))

matrix.SetImage(image)
input("Press Enter to exit...")
matrix.Clear()
