import queue
import time
import json
import esp32serialMonitoring
import matrixDisplay
import usbStorageDetec
import os

g: int= 0


serial_thread = esp32serialMonitoring.start()

usb_thread = usbStorageDetec.start()

matrixDisplay.initMatrix()

matrix_thread = None

currentTime :float= time.monotonic()
pastTime :float= 0

json_to_esp32 :dict = {
    "matrix": None,
    "usb": None,
    "main_debug": None
}

past_json :dict = None

def matrix_debug(message :str):
    json_to_esp32["matrix"] = message

def usb_debug(message :str):
    json_to_esp32["usb"] = message

def main_debug(message:str):
    json_to_esp32["main_debug"] = message

print("Script started.")
main_debug("Script started.")

def debugCheck() -> None:
    try:
        matrix_stat :str = matrixDisplay.matrix_output.get_nowait()
        print(f"Matrix status: {matrix_stat}")
        matrix_debug(matrix_stat)
    except queue.Empty:
        pass
    try:
        usb_stat :str = usbStorageDetec.usb_output.get_nowait()
        print(f"usb status: {usb_stat}")
        usb_debug(usb_stat)
    except queue.Empty:
        pass


def shutdownPrint() -> None:
    print("Shutdown Recieved\n")
    matrixDisplay.shutdown()
    time.sleep(10)
    print("Python effective UID:", os.geteuid())
    print("Shutting down, bye bye!")
    pass

def rebootPrint() -> None:
    print("Reboot Recieved\n")
    matrixDisplay.reboot()
    time.sleep(10)
    print("Python effective UID:", os.geteuid())
    print("Rebooting, bye bye!")
    pass

def stopMatrixVideo(placeholder :str) -> None:
    global matrix_thread

    print("Stopping video playback.")

    main_debug("Stopping video playback.")

    matrixDisplay.stop_playing()

    if matrix_thread is not None:

        matrix_thread.join(timeout=3)

        if matrix_thread.is_alive():

            print("Playback thread is still stopping.")

            return
        
        matrix_thread = None

def playMatrixVideo(path_to_video :str) -> None:    
    global matrix_thread

    print(f"Playing video: {path_to_video}")
    main_debug(f"Playing video: {path_to_video}")

    try:
        matrixDisplay.stop_event.clear()
        matrix_thread = matrixDisplay.start(path_to_video)
        

    except Exception as e:

        print(f"Error playing video '{path_to_video}': {e}")
        main_debug(f"Error playing video '{path_to_video}': {e}")

def matrixSleep(egg) -> None:
    matrixDisplay.sleep_picture()

def matrixBrightness(brightness :str) -> None:
    try:
        int_bright = int(brightness)
        print(f"converting to int value{int_bright}")
    except ValueError as e:
        print(f"Variable {brightness} is most likely not an integer. Brightness only supports integers. Error {e}")
        main_debug(f"Variable {brightness} is most likely not an integer. Brightness only supports integers. Error {e}")
        return
    matrixDisplay.adjustBrightness(int_bright)

def displayImage(path_to_image :str):

    if matrixDisplay.display_the_image(path_to_image):
        print(f"Displaying {path_to_image}")
        main_debug(f"Displaying {path_to_image}")
    else:
        print(f"{path_to_image} is most likely corrupted or not an image.")
        main_debug(f"{path_to_image} is most likely corrupted or not an image.")


def matrixFunctions(command :str, argument :str = ""):
    handler :callable = matrix_commands.get(command)
    if handler is not None:
        try:
            handler(argument)
        except Exception as e:
            print(f"Error executing matrix command '{command}': {e}")
            main_debug(f"Error executing matrix command '{command}': {e}")
    else:
        print(f"No handler found for matrix command '{command}'")
        main_debug(f"Error executing matrix command '{command}': {e}")

def usbMount(argument):
    if usbStorageDetec.mount_drive(argument):
        print(f"Mounted {argument} to /media/usb-drive")
        main_debug(f"Mounted {argument} to /media/usb-drive")
    else:
        print(f"Something went wrong trying to mount {argument}. Check logs")
        main_debug(f"Something went wrong trying to mount {argument}. Check logs")

def usbUmount(argument):
    if usbStorageDetec.umount_drive():
        print(f"Unmounted /media/usb-drive")
        main_debug(f"Unmounted /media/usb-drive")
    else:
        print(f"Something went wrong trying to unmount {argument}. Check logs")
        main_debug(f"Something went wrong trying to unmount {argument}. Check logs")



def usbFunctions(command :str, argument :str = ""):
    handler :callable = usb_commands.get(command)
    if handler is not None:
        try:
            handler(argument)
        except Exception as e:
            print(f"Error executing usb command '{command}': {e}")
            main_debug(f"Error executing usb command '{command}': {e}")
    else:
        print(f"No handler found for usb command '{command}'")
        main_debug(f"No handler found for usb command '{command}'")

def sendDebugJson():
    global json_to_esp32
    global past_json
    past_json = json_to_esp32.copy()
    json_to_send = json.dumps(json_to_esp32)
    esp32serialMonitoring.writeSerial(json_to_send)


matrix_commands :dict = {
    "play": playMatrixVideo,
    "brightness": matrixBrightness,
    "br": matrixBrightness,
    "stop": stopMatrixVideo,
    "display": displayImage,
    "sleep": matrixSleep
}

usb_commands :dict = {
    "mount": usbMount,
    "unmount": usbUmount
}

commands :dict = {
    "shutdown": shutdownPrint,
    "reboot" : rebootPrint,
    "matrix": matrixFunctions,
    "usb": usbFunctions,
    "Waiting for ESP32...": lambda: None  
}


try:
    while True: #Infinite loop, sort of like void loop
        try:
            debugCheck()
            fromEsp :str= esp32serialMonitoring.serial_output.get(timeout=0.01)
            parts = fromEsp.split("|")

            cmd = parts[0]
            args = parts[1:]

            if fromEsp:
                print("From ESP32", fromEsp)
                if cmd:
                    handler :callable = commands.get(cmd)
                    if handler is not None:
                        try:
                            handler(*args)
                        except Exception as e:
                            print(f"Error executing command '{cmd}': {e}")
                            main_debug(f"Error executing command '{cmd}': {e}")
                    else: 
                        main_debug(f"No handler found for command '{cmd}'")
                        print(f"No handler found for command '{cmd}'")
        except queue.Empty:
            pass
        if json_to_esp32 != past_json:
            sendDebugJson()
        currentTime :float= time.monotonic()
        if (currentTime-pastTime) >= 30:
            g+=1
            pastTime = currentTime
            main_debug("Pi Connected "+str(g))
            print("hello world", g)
        
        
except KeyboardInterrupt:
    pass

finally:
    print("byteyyrtrey")
    esp32serialMonitoring.stop_event.set()
    matrixDisplay.stop_event.set()
    serial_thread.join(timeout=3)