from gpiozero import LED
import serial
import time
import subprocess

blue = LED(17)
g = 0
#sets led pin to 17

ser = serial.Serial(
    "/dev/serial0",
    115200,
    timeout=0.1
)

currentTime = time.monotonic()
pastTime = 0

def serialReading():
    try:
        while True: 
            if ser.in_waiting > 0:
                msg = ser.readline().decode(
                    "utf-8", errors="replace"
                ).strip()
                if msg:
                    if msg == "ping":
                        blue.on()
                        print("Recieved ping, sending pong.")
                        ser.write(b"pong\n")
                        blue.off()
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
                            subprocess.run(["sudo", "-n", "./scripts/ShutdownScript.sh"])
                    except subprocess.CalledProcessError:
                        print("Failed to run shutdown command.")
            #cheese = input("Send something to ESP32!: ")
            #ser.write((cheese + "\n").encode("utf-8"))
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