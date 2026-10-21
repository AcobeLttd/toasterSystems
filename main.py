import queue
import time
import esp32serialMonitoring
import matrixDisplay
import matrixVideo
import os

g: int= 0


serial_thread = esp32serialMonitoring.start()

matrixDisplay.initMatrix()

matrix_thread = matrixDisplay.start()

decoder_thread = None

currentTime :float= time.monotonic()
pastTime :float= 0

print("Script started.")

def matrixCheck() -> None:
    try:
        matrix_stat :str = matrixDisplay.matrix_output.get_nowait()
        print(f"Matrix status: {matrix_stat}")
        esp32serialMonitoring.writeSerial(f"Matrix status: {matrix_stat}")
    except queue.Empty:
        pass
    try:
        matrix_decode :str = matrixVideo.video_debug_output.get_nowait()
        print(f"Decoder info: {matrix_decode}")
        esp32serialMonitoring.writeSerial(f"Matrix decode: {matrix_decode}")
    except queue.Empty:
        pass


def shutdownPrint() -> None:
    print("Shutdown Recieved\n")
    time.sleep(20)
    print("Python effective UID:", os.geteuid())
    print("Shutting down, bye bye!")
    currentTime :float= time.monotonic()
    pass

def playMatrixVideo(path_to_video :str) -> None:    
    if path_to_video == "stop":
        print("Stopping video playback.")
        esp32serialMonitoring.writeSerial("Stopping video playback.")
        matrixVideo.stop_event.set()
        return
    
    print(f"Playing video: {path_to_video}")
    esp32serialMonitoring.writeSerial(f"Playing video: {path_to_video}")
    try:

        matrixDisplay.stop_matrix.clear()
        matrixVideo.stop_event.clear()
        matrixVideo.decode(path_to_video)

    except Exception as e:
        
        print(f"Error playing video '{path_to_video}': {e}")
        esp32serialMonitoring.writeSerial(f"Error playing video '{path_to_video}': {e}")

def matrixBrightness(brightness :str) -> None:
    matrixDisplay.matrix_brightness.put(int(brightness))

def matrixFunctions(command :str, argument :str, *args :str):
    if command == "play":
        playMatrixVideo(argument)        
    elif command in ("brightness", "br"):
        matrixBrightness(argument)
    else:
        print(f"{command} not recognized as a command.")
        esp32serialMonitoring.writeSerial(f"{command} not recognized as a command for matrix.")
        pass

commands :dict = {
    "shutdown": shutdownPrint,
    "matrix": matrixFunctions,
    "Waiting for ESP32...": lambda: None  
}



try:
    while True: 
        try:
            matrixCheck()
            fromEsp :str= esp32serialMonitoring.serial_output.get(timeout=0.01)
            parts = fromEsp.split("|")

            cmd = parts[0]
            args = parts[1:]

            if fromEsp:
                print("From ESP32", fromEsp)
                if cmd:
                    handler :callable = commands.get(cmd)
                    if handler is not None:
                        try:
                            handler(*args)
                        except Exception as e:
                            print(f"Error executing command '{cmd}': {e}")
                            esp32serialMonitoring.writeSerial(f"Error executing command '{cmd}': {e}")
                    else: 
                        print(f"No handler found for command '{cmd}'")
                        esp32serialMonitoring.writeSerial(f"No handler found for command '{cmd}'")
        except queue.Empty:
            pass
        currentTime :float= time.monotonic()
        if (currentTime-pastTime) >= 30:
            g+=1
            pastTime = currentTime
            esp32serialMonitoring.writeSerial("Pi Connected "+str(g))
            print("hello world", g)
        
        
except KeyboardInterrupt:
    pass

finally:
    print("byteyyrtrey")
    esp32serialMonitoring.stop_event.set()
    matrixDisplay.stop_matrix.set()
    matrixVideo.stop_event.set()
    serial_thread.join(timeout=3)
    matrix_thread.join(timeout=3)
    matrix_thread.join(timeout=3)