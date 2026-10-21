import subprocess
import threading
import queue
from PIL import Image

frame_queue  = queue.Queue(maxsize=1)

video_debug_output :queue.Queue[str] = queue.Queue()

stop_event = threading.Event()

decoder_thread = None

WIDTH, HEIGHT = 64, 32
FPS = 60
FRAME_SIZE = WIDTH * HEIGHT * 3

def send_frames(frame):
    try:
        frame_queue.put_nowait(frame)
    except queue.Full:
        try:
            frame_queue.get_nowait()  # Drop stale frame
        except queue.Empty:
            pass
        frame_queue.put_nowait(frame)

def playthe_video(path_to_video: str) -> None:
    print("does it get here?")
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
    except Exception as e:
            video_debug_output.put(f"Decoder error: {e}")
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
            send_frames(frame)
            

            
    finally:
        video_debug_output.put("Cleaning up FFmpeg and clearing matrix") # code to be changed to have it fade to something else or black before fading in another animation. To be determined.
        print("Cleaning up FFmpeg")

    
        print("Force killing FFmpeg")
        process.kill()
        process.wait()

def decode(path_to_video) -> threading.Thread:
    print("decoding started")
    global decoder_thread
    stop_event.clear()

    if decoder_thread is not None and decoder_thread.is_alive():
        raise RuntimeError("A decoder is already running; stop and join it first.")


    decoder_thread = threading.Thread(target=playthe_video, args=(path_to_video,),daemon=False,)
    decoder_thread.start()
    return decoder_thread
