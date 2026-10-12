from gpiozero import LED
import serial
from time import sleep
import subprocess

blue = LED(17)
g = 0
#sets led pin to 17

ser = serial.Serial(
    "/dev/serial0",
    115200,
    timeout=0.1
)

try:
    while True: #Infinite loop, sort of like void loop
        if ser.in_waiting > 0:
            msg = ser.readline().decode(
                "utf-8", errors="replace"
            ).strip()
            if msg:
                print("From ESP32", msg)
                blue.toggle()
                try:
                    if msg == "shutdown":
                        subprocess.run(["sudo", "shutdown", "-h", "now"])
                except subprocess.CalledProcessError:
                    print("Failed to run shutdown command.")
        #cheese = input("Send something to ESP32!: ")
        #ser.write((cheese + "\n").encode("utf-8"))
        ser.write(b"thingi \n")
        sleep(1)
        g+=1
        print("hello world", g)
except KeyboardInterupt:
    pass

finally:
    ser.close()