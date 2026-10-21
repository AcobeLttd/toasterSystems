import threading
import queue
import matrixVideo
from PIL import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions

stop_event = threading.Event()

stop_video = threading.Event()

send_command :queue.Queue[str] = queue.Queue()

matrix_output :queue.Queue[str] = queue.Queue()

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
    global matrix
    matrix.Clear()
    
    offscreen = matrix.CreateFrameCanvas()

    display_image = Image.new("RGB", (128, 32), (0, 0, 0))

    while not stop_video.is_set():
        try:
            frame = matrixVideo.frame_quene.get_nowait()
        except queue.Empty:
            frame = Image.new("RGB", (128, 32), (0, 0, 0))
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


def stop():
    stop_video.set()


commands :dict = {
    "play": matrixVideo.playthe_video,
}


def matrixHandlingThread():
    while not stop_event.is_set():
        try:
            
            fromMain:str = send_command.get_nowait() 
            parts = fromMain.split("|")

            cmd = parts[0]
            args = parts[1:]

            if cmd:
                handler :callable = commands.get(cmd)
                if handler is not None:
                    try:
                        handler(*args)
                    except Exception as e:
                       
                        matrix_output.put(f"Error executing command '{cmd}': {e}")

                else: 
                        
                    matrix_output.put(f"No handler found for command '{cmd}'")

        except queue.Empty:
            pass
        displayMatrix()



def start() -> threading.Thread:
    thread = threading.Thread(target=matrixHandlingThread, daemon=False)
    thread.start()
    return thread

if __name__ == "__main__":
    video_path = "./test-media/theAppleThatIsBad.mp4"
    start(video_path)