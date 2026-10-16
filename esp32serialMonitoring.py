import queue
import threading
import serial
import time
import subprocess

serial_output = queue.Queue()

serial_output.put("Waiting for ESP32...")

serial_to_send = queue.Queue()

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
            try:
                message = serial_to_send.get_nowait()
                print("Trying to write serial: ", message)
                ser.write((message + "\n").encode("utf-8"))
            except queue.Empty:
                pass
            if ser.in_waiting > 0:
                msg = ser.readline().decode(
                    "utf-8", errors="replace"
                ).strip()
                serial_output.put(msg)
                if msg:
                    if msg == "ping":
                        print("Recieved ping, sending pong.")
                        ser.write(b"pong\n")
                    elif msg == "shutdown":
                        try:
                            ser.write(b"Shutdown Recieved\n")
                            time.sleep(20)
                            ser.write(b"Shutting down\n")
                            subprocess.run(["sudo", "-n", "./scripts/ShutdownScript.sh"])
                        except subprocess.CalledProcessError:
                            print("Failed to run shutdown command.")
    except Exception as e:
        print(f"Serial monitor error{e}")
        pass

    finally:
        ser.close()
def writeSerial(message):
    serial_to_send.put(message)

def start():
    thread = threading.Thread(target=serialReading, daemon=False)
    thread.start()
    return thread