import subprocess
import threading
import queue
from PIL import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions

stop_event = threading.Event()

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


def playthe_video(path_to_video: str) -> None:
    global matrix

    matrix_output.put(f"Starting video playback for: {path_to_video}")
    
    offscreen = matrix.CreateFrameCanvas()

    display_image = Image.new("RGB", (128, 32), (0, 0, 0))
    try:
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
    except subprocess.CalledProcessError as e:
        matrix_output.put(f"Error executing ffmpeg command: {e}")
        return

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        bufsize=FRAME_SIZE * 6,
    )


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
 
    finally:
        matrix_output.put("Cleaning up FFmpeg and clearing matrix") # code to be changed to have it fade to something else or black before fading in another animation. To be determined.
        print("Cleaning up FFmpeg")

    
        print("Force killing FFmpeg")
        process.kill()
        process.wait()

        print("Clearing matrix")
        matrix.Clear()


def stop():
    stop_event.set()


commands :dict = {
    "play": playthe_video,
}


def matrixHandlingThread():
    while not stop_event.is_set():
        try:
            
            fromMain:str = send_command.get_nowait() 
            parts = cmd.split("|")

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



def start() -> threading.Thread:
    thread = threading.Thread(target=matrixHandlingThread, daemon=False)
    thread.start()
    return thread

if __name__ == "__main__":
    video_path = "./test-media/theAppleThatIsBad.mp4"
    start(video_path)