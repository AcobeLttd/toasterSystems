from gpiozero import LED
import queue
import time
import esp32serialMonitoring

blue = LED(17)
g = 0
#sets led pin to 17

serial_thread = esp32serialMonitoring.start()

currentTime = time.monotonic()
pastTime = 0

print("Script started.")

def ledOff():
    blue.off()
    esp32serialMonitoring.writeSerial("L F")

def ledOn():
    blue.on()
    esp32serialMonitoring.writeSerial("L T")

def shutdownPrint():
    blue.blink()
    print("Shutdown Recieved\n")
    time.sleep(20)
    blue.on()
    print("Shutting down, bye bye!")
    currentTime = time.monotonic()
    pass

def pinging(): #pinging handled by esp32serialMonitoring.py. This is just to stop errors from occuring.
    pass

commands = {
    "lfalse": ledOn,
    "ltrue": ledOff,
    "shutdown": shutdownPrint,
    "ping": pinging
}



try:
    while True: #Infinite loop, sort of like void loop
        try:
            msg = esp32serialMonitoring.serial_output.get(timeout=0.01)
            if msg:
                print("From ESP32", msg)
                handler = commands.get(msg)
                if handler is not None:
                    try:
                        handler()
                    except Exception as e:
                        print(f"Error executing command '{msg}': {e}")
                else: 
                    print(f"No handler found for command '{msg}'")
        except queue.Empty:
            pass
        currentTime=time.monotonic()
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