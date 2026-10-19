import subprocess
import time
from PIL import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions

WIDTH, HEIGHT = 64, 32
FPS = 60
FRAME_SIZE = WIDTH * HEIGHT * 3

options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 2
options.parallel = 1
options.hardware_mapping = "regular"

global matrix
matrix = RGBMatrix(options=options)
global offscreen
offscreen = matrix.CreateFrameCanvas()
global display_image
display_image = Image.new("RGB", (128, 32), (0, 0, 0))

def playthe_video(path_to_video: str):
    cmd = [
        "ffmpeg",
        "-hide_banner", "-loglevel", "error",
        "-re",
        "-i", path_to_video,
        "-an",
        "-vf", "scale=64:32:flags=bicubic,fps=60",
        "-pix_fmt", "rgb24",
        "-f", "rawvideo",
        "pipe:1",
    ]


    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        bufsize=FRAME_SIZE * 6,
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

            display_image.paste(frame, (0, 0))


            mirrored = frame.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            display_image.paste(mirrored, (64, 0))

            offscreen.SetImage(display_image)
            offscreen = matrix.SwapOnVSync(offscreen)

    finally:
        process.terminate()
        process.wait()
        matrix.Clear()

if __name__ == "__main__":
    video_path = "./test-media/theAppleThatIsBad.mp4"
    playthe_video(video_path)