import subprocess
import time
from PIL import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions

WIDTH, HEIGHT = 128, 32
FPS = 60
FRAME_SIZE = WIDTH * HEIGHT * 3

options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 2
options.parallel = 1
options.hardware_mapping = "regular"

matrix = RGBMatrix(options=options)

cmd = [
    "ffmpeg",
    "-hide_banner", "-loglevel", "error",
    "-re",
    "-i", "./test-media/theAppleThatIsBad.mp4",
    "-an",
    "-vf", "scale=128:32:flags=bicubic,fps=60",
    "-pix_fmt", "rgb24",
    "-f", "rawvideo",
    "pipe:1",
]

process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    bufsize=FRAME_SIZE * 4,
)

try:
    while True:
        data = bytearray()

        while len(data) < FRAME_SIZE:
            chunk = process.stdout.read(FRAME_SIZE - len(data))
            if not chunk:
                break
            data.extend(chunk)

        if len(data) != FRAME_SIZE:
            break

        frame = Image.frombytes("RGB", (WIDTH, HEIGHT), bytes(data))
        matrix.SetImage(frame)

finally:
    process.terminate()
    process.wait()
    matrix.Clear()