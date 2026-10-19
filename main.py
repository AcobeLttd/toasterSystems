from gpiozero import LED
import queue
import time
import esp32serialMonitoring

blue = LED(17)
g: int= 0
#sets led pin to 17

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

def shutdownPrint() -> None:
    blue.blink()
    print("Shutdown Recieved\n")
    time.sleep(20)
    blue.on()
    print("Shutting down, bye bye!")
    currentTime :float= time.monotonic()
    pass


commands = {
    "lfalse": ledOn,
    "ltrue": ledOff,
    "shutdown": shutdownPrint,
    "Waiting for ESP32...": lambda: None  
}



try:
    while True: #Infinite loop, sort of like void loop
        try:
            msg :str= esp32serialMonitoring.serial_output.get(timeout=0.01)
            if msg:
                print("From ESP32", msg)
                handler :callable = commands.get(msg)
                if handler is not None:
                    try:
                        handler()
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