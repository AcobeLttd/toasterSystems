from gpiozero import LED
import queue
import time
import esp32serialMonitoring
import matrxiVideoPlayback


blue = LED(12)
g: int= 0
#sets led pin to 12

serial_thread = esp32serialMonitoring.start()

currentTime :float= time.monotonic()
pastTime :float= 0

print("Script started.")

def ledOff() -> None:
    blue.off()
    esp32serialMonitoring.writeSerial("L F")

def ledOn() -> None:
    blue.on()
    esp32serialMonitoring.writeSerial("L T")

def ledStat(state :str):
    if state == "on":
        ledOn()
    elif state == "off":
        ledOff()
    else:
        print(f"Unknown state '{state}' for ledStat command.")

def shutdownPrint() -> None:
    blue.blink()
    print("Shutdown Recieved\n")
    time.sleep(20)
    blue.on()
    print("Shutting down, bye bye!")
    currentTime :float= time.monotonic()
    pass

def playMatrixVideo(path_to_video :str) -> None:    
    print(f"Playing video: {path_to_video}")
    esp32serialMonitoring.writeSerial(f"Playing video: {path_to_video}")
    matrxiVideoPlayback.playthe_video(path_to_video)


commands :dict = {
    "l": ledStat,
    "shutdown": shutdownPrint,
    "play matrix": playMatrixVideo,
    "Waiting for ESP32...": lambda: None  
}



try:
    while True: #Infinite loop, sort of like void loop
        try:
            fromEsp :str= esp32serialMonitoring.serial_output.get(timeout=0.01)
            lowerCaseEsp:str= fromEsp.lower()
            parts = lowerCaseEsp.split("|")

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