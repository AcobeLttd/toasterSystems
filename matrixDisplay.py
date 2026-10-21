import subprocess
import threading
import queue
from PIL import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions

stop_event = threading.Event()

default_brightness :int=60

matrix = None

current_frame = Image.new("RGB", (128, 32), (0, 0, 0))



WIDTH, HEIGHT = 64, 32
FPS = 60
FRAME_SIZE = WIDTH * HEIGHT * 3


def start_up():
    global matrix
    image = Image.open("./test-media/blåhaj.png").convert("RGB")
    image = image.resize((64, 32), Image.Resampling.BICUBIC)
    image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

    display_on_both(image)

def initMatrix() -> None:
    global matrix
    global offscreen
    global display_image

    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 64
    options.chain_length = 2
    options.parallel = 1
    options.hardware_mapping = "regular"
    options.brightness = 60

    matrix = RGBMatrix(options=options)
    offscreen = matrix.CreateFrameCanvas()
    
    display_image = Image.new("RGB", (128, 32), (0, 0, 0))
    
    start_up()


def adjustBrightness(brightness: int) -> None:
    global matrix
    brightness = max(0, min(100, brightness))
    print(f"recieved in matrix code {brightness}")
    matrix.brightness = brightness
    display_on_both(current_frame)

def ffmpeg_decode(path_to_video: str):
    global process
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
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            bufsize=FRAME_SIZE * 6,
        )
            
    except subprocess.CalledProcessError as e:
            print(f"Error executing ffmpeg command: {e}")
            return
    
def display_on_both(frames :Image.Image):
    global offscreen
    global display_image
    global current_frame
    current_frame = frames
    
    display_image.paste(frames, (0, 0))
    mirrored = frames.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    display_image.paste(mirrored, (64, 0))
    
    offscreen.SetImage(display_image)
    offscreen = matrix.SwapOnVSync(offscreen)


def playthe_video(path_to_video: str) -> None:
    global matrix
    global process
    global offscreen
    global display_image

    print(f"Starting video playback for: {path_to_video}")
    
    
    ffmpeg_decode(path_to_video)


    try:
        while not stop_event.is_set():

            data = bytearray()

            while len(data) < FRAME_SIZE:
                chunk = process.stdout.read(FRAME_SIZE - len(data))
                if not chunk:
                    break
                data.extend(chunk)

            if len(data) != FRAME_SIZE:
                break 

            frame = Image.frombytes("RGB", (WIDTH, HEIGHT), bytes(data))
            display_on_both(frame)

 
    finally:
        print("Cleaning up FFmpeg")

    
        print("Force killing FFmpeg")
        process.kill()
        process.wait()

        print("Clearing matrix")
        matrix.Clear()

def start(path_to_video: str) -> threading.Thread:
    print(f"Starting video playback thread for: {path_to_video}")
    thread = threading.Thread(target=playthe_video, args=(path_to_video,), daemon=False)
    thread.start()
    return thread

if __name__ == "__main__":
    video_path = "./test-media/theAppleThatIsBad.mp4"
    start(video_path)