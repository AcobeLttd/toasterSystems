from gpiozero import LED
import queue
import time
import subprocess
import esp32serialMonitoring

blue = LED(17)
g = 0
#sets led pin to 17

serial_thread = esp32serialMonitoring.start()

currentTime = time.monotonic()
pastTime = 0

print("Script started.")

try:
    while True: #Infinite loop, sort of like void loop
        try:
            msg = esp32serialMonitoring.serial_output.get_nowait()
            if msg:
                print("From ESP32", msg)
                if msg == "lfalse":
                    blue.off()
                elif msg == "ltrue":
                    blue.on()
                try:
                    if msg == "shutdown":
                        blue.blink()
                        print("Shutdown Recieved\n")
                        time.sleep(20)
                        blue.on()
                        print("Shutting down, bye bye!")
                        subprocess.run(["sudo", "-n", "./scripts/ShutdownScript.sh"], check=True)
                except subprocess.CalledProcessError:
                    print("Failed to run shutdown command.")
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