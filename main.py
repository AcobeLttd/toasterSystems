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
    except queue.Empty:
        pass


def shutdownPrint() -> None:
    print("Shutdown Recieved\n")
    matrixDisplay.shutdown()
    time.sleep(10)
    print("Python effective UID:", os.geteuid())
    print("Shutting down, bye bye!")
    currentTime :float= time.monotonic()
    pass

def stopMatrixVideo(placeholder :str) -> None:
    global matrix_thread

    print("Stopping video playback.")

    esp32serialMonitoring.writeSerial("Stopping video playback.")

    matrixDisplay.stop_playing()

    if matrix_thread is not None:

        matrix_thread.join(timeout=3)

        if matrix_thread.is_alive():

            print("Playback thread is still stopping.")

            return
        
        matrix_thread = None

    if matrix_thread is not None and matrix_thread.is_alive():

        matrixDisplay.stop_event.set()
        matrix_thread.join(timeout=3)

def playMatrixVideo(path_to_video :str) -> None:    
    global matrix_thread

    print(f"Playing video: {path_to_video}")
    esp32serialMonitoring.writeSerial(f"Playing video: {path_to_video}")

    try:
        matrix_thread = matrixDisplay.start(path_to_video)
        matrixDisplay.stop_event.clear()

    except Exception as e:

        print(f"Error playing video '{path_to_video}': {e}")
        esp32serialMonitoring.writeSerial(f"Error playing video '{path_to_video}': {e}")

def matrixBrightness(brightness :str) -> None:
    try:
        int_bright = int(brightness)
        print(f"converting to int value{int_bright}")
    except ValueError as e:
        print(f"Variable {brightness} is most likely not an integer. Brightness only supports integers. Error {e}")
        esp32serialMonitoring.writeSerial(f"Variable {brightness} is most likely not an integer. Brightness only supports integers. Error {e}")
        return
    matrixDisplay.adjustBrightness(int_bright)

def displayImage(path_to_image :str):

    if matrixDisplay.display_the_image(path_to_image):
        print(f"Displaying {path_to_image}")
        esp32serialMonitoring.writeSerial(f"Displaying {path_to_image}")
    else:
        print(f"{path_to_image} is most likely corrupted or not an image.")
        esp32serialMonitoring.writeSerial(f"{path_to_image} is most likely corrupted or not an image.")


def matrixFunctions(command :str, argument :str = ""):
    handler :callable = matrix_commands.get(command)
    if handler is not None:
        try:
            handler(argument)
        except Exception as e:
            print(f"Error executing matrix command '{command}': {e}")
    else:
        print(f"No handler found for matrix command '{command}'")



matrix_commands :dict = {
    "play": playMatrixVideo,
    "brightness": matrixBrightness,
    "br": matrixBrightness,
    "stop": stopMatrixVideo,
    "display": displayImage
}

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
                    else: 
                        print(f"No handler found for command '{cmd}'")
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