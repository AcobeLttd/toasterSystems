import threading
import queue
import matrixVideo
from PIL import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions


stop_matrix = threading.Event()

send_command :queue.Queue[str] = queue.Queue()

matrix_output :queue.Queue[str] = queue.Queue()

frame = queue.Queue()
frame.put(Image.new("RGB", (128, 32), (0, 0, 0)))

default_brightness :int=60

matrix = None

matrix_brightness : queue.Queue[int]= queue.Queue()
matrix_brightness.put(default_brightness)

WIDTH, HEIGHT = 64, 32
FPS = 60
FRAME_SIZE = WIDTH * HEIGHT * 3

def initMatrix() -> None:
    global matrix

    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 64
    options.chain_length = 2
    options.parallel = 1
    options.hardware_mapping = "regular"
    options.brightness = 60

    matrix = RGBMatrix(options=options)
    matrix_output.put("Matrix initialized")

def adjustBrightness(brightness: int) -> None:
    global matrix
    brightness = max(0, min(100, brightness))
    matrix.brightness = brightness


def displayMatrix() -> None:
    print("Does it get to display matrix?")
    global matrix
    matrix.Clear()
    
    offscreen = matrix.CreateFrameCanvas()

    display_image = Image.new("RGB", (128, 32), (0, 0, 0))

    while not stop_matrix.is_set():
        try:
            frame = matrixVideo.frame_queue.get_nowait()
        except queue.Empty:
            pass

        display_image.paste(frame, (0, 0))

        try:
            bright = matrix_brightness.get_nowait()
            adjustBrightness(bright)
        except queue.Empty:
            pass

        mirrored = frame.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        display_image.paste(mirrored, (64, 0))

        offscreen.SetImage(display_image)
        offscreen = matrix.SwapOnVSync(offscreen)

def stop_video() -> None:
    matrixVideo.stop_event.set()

def stop() -> None:
    stop_matrix.set()

def start() -> threading.Thread:
    thread = threading.Thread(target=displayMatrix, daemon=False)
    thread.start()
    return thread

if __name__ == "__main__":
    initMatrix()
    video_path = "./test-media/theAppleThatIsBad.mp4"
    start()
    matrixVideo.decode(video_path)