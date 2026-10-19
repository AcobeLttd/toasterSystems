from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw

options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 2
options.parallel = 1
options.hardware_mapping = "regular"

matrix = RGBMatrix(options=options)

# Black canvas covering both panels
canvas = Image.new("RGB", (128, 32), (0, 0, 0))
draw = ImageDraw.Draw(canvas)

# Panel 1: red rectangle
draw.rectangle((5, 5, 25, 25), fill=(255, 0, 0))

# Panel 2: green rectangle
draw.rectangle((69, 5, 89, 25), fill=(0, 255, 0))

matrix.SetImage(canvas)

input("Press Enter to clear the display...")
matrix.Clear()