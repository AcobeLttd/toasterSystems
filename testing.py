from gpiozero import LED
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
        if ser.in_waiting > 0:
            msg = esp32serialMonitoring.serialReading.get_nowait()
            if msg:
                print("From ESP32", msg)
                elif msg == "lfalse":
                    blue.off()
                elif msg == "ltrue":
                    blue.on()
                try:
                    if msg == "shutdown":
                        blue.blink()
                        ser.write(b"Shutdown Recieved\n")
                        time.sleep(20)
                        blue.on()
                        ser.write(b"Shutting down\n")
                        print("Shutting down, bye bye!")
                        subprocess.run(["sudo", "-n", "./scripts/ShutdownScript.sh"], check=True)
                except subprocess.CalledProcessError:
                    print("Failed to run shutdown command.")
        currentTime=time.monotonic()
        if (currentTime-pastTime) >= 30:
            g+=1
            pastTime = currentTime
            ser.write(("Pi Connected "+str(g)+"\n").encode("utf-8"))
            print("hello world", g)
        
        
except KeyboardInterrupt:
    pass

finally:
    ser.close()