
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
#image = image.resize((64, 32), Image.Resampling.LANCZOS)

#background = Image.new("RGBA", image.size, (0, 0, 0, 255))
#image = Image.alpha_composite(background, image).convert("RGB")


# Composite transparency onto black BEFORE resizing

background = Image.new("RGBA", image.size, (0, 0, 0, 255))
image = Image.alpha_composite(background, image).convert("RGB")

# Resize only after transparency is removed
image = image.resize((64, 32), Image.Resampling.LANCZOS)

canvas = Image.new("RGB", (128, 32))

mirrored = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

canvas.paste(mirrored, (0, 0))
canvas.paste(image, (64, 0))


matrix.SetImage(canvas)
input("Press Enter to exit...")
matrix.Clear()
