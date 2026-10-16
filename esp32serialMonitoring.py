import quene
import serial
import time
import subprocess


currentTime = time.monotonic()
pastTime = 0

def serialReading():
    ser = serial.Serial(
        "/dev/serial0",
        115200,
        timeout=0.1
    )
    try:
        while True: 
            if ser.in_waiting > 0:
                msg = ser.readline().decode(
                    "utf-8", errors="replace"
                ).strip()
                if msg:
                    if msg == "ping":
                        print("Recieved ping, sending pong.")
                        ser.write(b"pong\n")
                    try:
                        if msg == "shutdown":
                            ser.write(b"Shutdown Recieved\n")
                            time.sleep(20)
                            ser.write(b"Shutting down\n")
                            print("Shutting down, bye bye!")
                            subprocess.run(["sudo", "-n", "./scripts/ShutdownScript.sh"])
                    except subprocess.CalledProcessError:
                        print("Failed to run shutdown command.")
                    return msg
    except KeyboardInterrupt:
        pass

    finally:
        ser.close()