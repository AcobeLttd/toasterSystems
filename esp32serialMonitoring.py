import queue
import threading
import serial
import time
import subprocess

serial_output = queue.Queue()
serial_output.put("Waiting for ESP32...")

stop_event = threading.Event()

ser = None

currentTime = time.monotonic()
pastTime = 0

def serialReading():
    global ser
    
    try:
        ser = serial.Serial(
                "/dev/serial0",
                115200,
                timeout=0.1
            )
        print("Serial started at 115200 baud rate.")
        while not stop_event.is_set(): 
            if ser.in_waiting > 0:
                msg = ser.readline().decode(
                    "utf-8", errors="replace"
                ).strip()
                serial_output.put(msg)
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
    except Exception as e:
        print(f"Serial monitor error{e}")
        pass

    finally:
        ser.close()
def writeSerial(message):
    if ser is not None and ser.is_open:
        try:
            ser.write((message + "\n").encode("utf-8"))
        except Exception as e:
            print(f"Error writing to serial: {e}")

def start():
    thread = threading.Thread(target=serialReading, daemon=False)
    thread.start()
    return thread