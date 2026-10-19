
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
# Make partially transparent pixels fully transparent,
# and fully opaque pixels fully opaque.
r, g, b, a = image.split()
a = a.point(lambda p: 255 if p >= 128 else 0)
image.putalpha(a)

# Composite onto black
background = Image.new("RGBA", image.size, (0, 0, 0, 255))
image = Image.alpha_composite(background, image).convert("RGB")


# Fit to one 64x32 panel
image = image.resize((64, 32), Image.Resampling.NEAREST)

canvas = Image.new("RGB", (128, 32), (0, 0, 0))
canvas.paste(image, (0, 0))
canvas.paste(image.transpose(Image.Transpose.FLIP_LEFT_RIGHT), (64, 0))


matrix.SetImage(canvas)
input("Press Enter to exit...")
matrix.Clear()
