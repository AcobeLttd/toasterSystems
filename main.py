import queue
import time
import esp32serialMonitoring
import matrixVideoPlayback

g: int= 0


serial_thread = esp32serialMonitoring.start()

currentTime :float= time.monotonic()
pastTime :float= 0

print("Script started.")


def shutdownPrint() -> None:
    print("Shutdown Recieved\n")
    time.sleep(20)
    print("Shutting down, bye bye!")
    currentTime :float= time.monotonic()
    pass

def playMatrixVideo(path_to_video :str) -> None:    
    if path_to_video == "stop":
        print("Stopping video playback.")
        esp32serialMonitoring.writeSerial("Stopping video playback.")
        matrixVideoPlayback.stop_event.set()
        return
    print(f"Playing video: {path_to_video}")
    esp32serialMonitoring.writeSerial(f"Playing video: {path_to_video}")
    try:
        matrix_thread = matrixVideoPlayback.start(path_to_video)
    except Exception as e:
        print(f"Error playing video '{path_to_video}': {e}")
        esp32serialMonitoring.writeSerial(f"Error playing video '{path_to_video}': {e}")

def matrixBrightness(brightness :str) -> None:
    matrixVideoPlayback.matrix_brightness.put(brightness)

def matrixFunctions(command :str, argument :str, *args :str):
    if args is not None:
        if command == "play":
            playMatrixVideo(argument)        
        elif command == "brightness" or "br":
            matrixBrightness(argument)
        else:
            print(f"{command} not recognized as a command.")
            esp32serialMonitoring.writeSerial(f"{command} not recognized as a command for matrix.")

commands :dict = {
    "shutdown": shutdownPrint,
    "matrix": matrixFunctions,
    "Waiting for ESP32...": lambda: None  
}



try:
    while True: #Infinite loop, sort of like void loop
        try:
            fromEsp :str= esp32serialMonitoring.serial_output.get(timeout=0.01)
            parts = fromEsp.split("|")

            msg = parts[0]
            args = parts[1:]

            if msg:
                print("From ESP32", msg)
                handler :callable = commands.get(msg)
                if handler is not None:
                    try:
                        handler(*args)
                    except Exception as e:
                        print(f"Error executing command '{msg}': {e}")
                else: 
                    print(f"No handler found for command '{msg}'")
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
    serial_thread.join(timeout=3)