import queue
import time
import esp32serialMonitoring
import matrixDisplay
import os

g: int= 0


serial_thread = esp32serialMonitoring.start()

matrixDisplay.initMatrix()

matrix_thread = None

currentTime :float= time.monotonic()
pastTime :float= 0

print("Script started.")

def matrixCheck() -> None:
    try:
        matrix_stat :str = matrixDisplay.matrix_output.get_nowait()
        print(f"Matrix status: {matrix_stat}")
        esp32serialMonitoring.writeSerial(f"Matrix status: {matrix_stat}")
    except queue.Empty():
        pass


def shutdownPrint() -> None:
    print("Shutdown Recieved\n")
    matrixDisplay.stop_event.set()
    time.sleep(20)
    print("Python effective UID:", os.geteuid())
    print("Shutting down, bye bye!")
    currentTime :float= time.monotonic()
    pass

def playMatrixVideo(path_to_video :str) -> None:    
    global matrix_thread
    if path_to_video == "stop":
        print("Stopping video playback.")
        esp32serialMonitoring.writeSerial("Stopping video playback.")
        matrixDisplay.stop_event.set()
        if matrix_thread is not None:
            matrix_thread.join(timeout=3)

            if matrix_thread.is_alive():
                print("Playback thread is still stopping.")
                return

            matrix_thread = None

        return
    
    print(f"Playing video: {path_to_video}")
    esp32serialMonitoring.writeSerial(f"Playing video: {path_to_video}")
    try:
        matrix_thread = matrixDisplay.start(path_to_video)
        matrixDisplay.stop_event.clear()
    except Exception as e:
        print(f"Error playing video '{path_to_video}': {e}")
        esp32serialMonitoring.writeSerial(f"Error playing video '{path_to_video}': {e}")

def matrixBrightness(brightness :str) -> None:
    matrixDisplay.matrix_brightness.put(int(brightness))

def matrixFunctions(command :str, argument :str, *args :str):
    if args is not None:
        if command == "play":
            playMatrixVideo(argument)        
        elif command == "brightness" or "br":
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
    while True: #Infinite loop, sort of like void loop
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
    matrixDisplay.stop_event.set()
    serial_thread.join(timeout=3)