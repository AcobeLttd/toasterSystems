import subprocess
import threading
import queue
from PIL import Image, UnidentifiedImageError
from rgbmatrix import RGBMatrix, RGBMatrixOptions

stop_event = threading.Event()

default_brightness :int=60

matrix_output = queue.Queue()

matrix = None

thread_matrix = None

current_frame = Image.new("RGB", (64, 32), (0, 0, 0))

current_image_path = "./test-media/blåhaj.png"

process = None



WIDTH, HEIGHT = 64, 32
FPS = 60
FRAME_SIZE = WIDTH * HEIGHT * 3

def shutdown():
    stop_event.set()
    global matrix
    image = Image.open("./test-media/horrifying.png").convert("RGB")
    image = image.resize((WIDTH, HEIGHT), Image.Resampling.BICUBIC)
    displayBlendImage(image)

    
    #shutdown animation or something idfk

def stop_the_thread():
    global thread_matrix
    stop_event.set()
    if thread_matrix is not None and thread_matrix.is_alive():
        thread_matrix.join()
    thread_matrix = None

def stop_playing():
    stop_the_thread()
    default()

def displayBlendImage(new :Image.Image):
    global current_frame

    duration = 4
    fps = 60

    image1 = new

    image2 = current_frame.copy()

    steps = max(1, int(duration*fps))

    for i in range (steps + 1):
        alpha = i / steps

        final_image = Image.blend(image2, image1, alpha)

        display_on_both(final_image)

def default():
    global current_image_path
    global current_frame

    image = Image.open(current_image_path).convert("RGB")
    image = image.resize((WIDTH, HEIGHT), Image.Resampling.BICUBIC)

    displayBlendImage(image)

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
    options.brightness = default_brightness

    matrix = RGBMatrix(options=options)
    offscreen = matrix.CreateFrameCanvas()
    
    display_image = Image.new("RGB", (128, 32), (0, 0, 0))
    
    default()


def adjustBrightness(brightness: int) -> None:
    global matrix
    brightness = max(0, min(100, brightness))
    print(f"recieved in matrix code {brightness}")
    matrix_output.put(f"recieved in matrix code {brightness}")
    matrix.brightness = brightness
    display_on_both(current_frame)

def detect_and_stop_ffmpeg():
    global process
    if process is not None and process.poll() is None:
        print("ffmepg still running. Terminating before starting new.")
        matrix_output.put("ffmepg still running. Terminating before starting new.")
        process.kill()
        process.wait()
        pass

def ffmpeg_decode(path_to_video: str):
    if isImage(path_to_video):
        print(f"Running stop command. {path_to_video} is either corrupted or not a video")
        matrix_output.put(f"Running stop command. {path_to_video} is either corrupted or not a video")
        return False
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

    detect_and_stop_ffmpeg()

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            bufsize=FRAME_SIZE * 6,
        )
            
    except subprocess.CalledProcessError as e:
            print(f"Error executing ffmpeg command: {e}")
            matrix_output.put(f"Error executing ffmpeg command: {e}")
            return False
    return True
    
def isImage(filePath: str) -> bool:
    try:
        with Image.open(filePath) as image:
            image.verify()
        return True
    except (UnidentifiedImageError, OSError, ValueError):
        return False

def display_the_image(path_to_image):
    stop_the_thread()
    global current_image_path
    current_image_path = path_to_image
    
    if isImage(current_image_path) is not True:
        print(f"Error executing. {current_image_path} is either corrupted or not an image")
        matrix_output.put(f"Error executing. {current_image_path} is either corrupted or not an image")
        return False
    
    image = Image.open(current_image_path).convert("RGB")
    image = image.resize((64, 32), Image.Resampling.BICUBIC)

    displayBlendImage(image)

    return True

    
def display_on_both(frames :Image.Image):
    global offscreen
    global display_image
    global current_frame
    current_frame = frames
    
    display_image.paste(frames, (64, 0))
    mirrored = frames.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    display_image.paste(mirrored, (0, 0))
    
    offscreen.SetImage(display_image)
    offscreen = matrix.SwapOnVSync(offscreen)


def playthe_video(path_to_video: str) -> None:
    global matrix
    global process
    global offscreen

    print(f"Starting video playback for: {path_to_video}")
    matrix_output.put(f"Starting video playback for: {path_to_video}")
    
    
    if ffmpeg_decode(path_to_video) is not True:
        print(f"problems with ffmpeg. {path_to_video} is not a video or corrupted. or ffmpeg error.")
        matrix_output.put(f"problems with ffmpeg. {path_to_video} is not a video or corrupted. or ffmpeg error.")
        return


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
        matrix_output.put("Fading last image.")
        print("Cleaning up FFmpeg")
        matrix_output.put("Cleaning up FFmpeg")

    
        print("Force killing FFmpeg")
        matrix_output.put("Force killing FFmpeg")
        process.kill()
        process.wait()


def start(path_to_video: str) -> threading.Thread:
    image = Image.new("RGB", (64, 32), (0, 0, 0))
    displayBlendImage(image);
    print(f"Starting video playback thread for: {path_to_video}")
    matrix_output.put(f"Starting video playback thread for: {path_to_video}")
    thread_matrix = threading.Thread(target=playthe_video, args=(path_to_video,), daemon=False)
    thread_matrix.start()
    return thread_matrix

if __name__ == "__main__":
    video_path = "./test-media/theAppleThatIsBad.mp4"
    start(video_path)