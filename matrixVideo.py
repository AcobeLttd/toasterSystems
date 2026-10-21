import subprocess
import queue
from PIL import Image

frame_quene  = queue.Queue(maxsize=1)

video_debug_output :queue.Queue[str] = queue.Queue()

WIDTH, HEIGHT = 64, 32
FPS = 60
FRAME_SIZE = WIDTH * HEIGHT * 3

def playthe_video(path_to_video: str) -> None:
    print(does it get here?)
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
        video_debug_output.put(f"Error executing ffmpeg command: {e}")
        return

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
            frame_quene.put(frame)
            try:
                frame_queue.put_nowait(frame)
            except queue.Full:
                try:
                    frame_queue.get_nowait()  # Drop stale frame
                except queue.Empty:
                    pass

                frame_queue.put_nowait(frame)

            
    finally:
        video_debug_output.put("Cleaning up FFmpeg and clearing matrix") # code to be changed to have it fade to something else or black before fading in another animation. To be determined.
        print("Cleaning up FFmpeg")

    
        print("Force killing FFmpeg")
        process.kill()
        process.wait()
