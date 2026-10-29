import queue
import threading
import subprocess
import json
import pyudev

usb_output = queue.Queue()

udev_version :int = pyudev.udev_version()

usb_output.put("udev version:", udev_version)

path_to_mount_point = "/media/usb-drive"

usb_information :dict = {
    "device": None,
    "partition": None,
    "debug": None
}

def send_json():
    global usb_information
    usb_output.put(usb_information)

def write_debug(message :str):
    usb_information["debug"] = message
    send_json()

def write_device(message :str):
    usb_information["device"] = message
    send_json()

def write_partition(message :str):
    usb_information["partition"] = message
    send_json()


def debug_the_things(device):
    if device.get("DEVTYPE") == "disk":
         write_device(device.device_node)
    elif device.get("DEVTYPE") == "partition":
        write_partition(device.device_node)
    else:
        print(f"wtf is this device.")
    print(
        "\naction =", device.action,
        "\ntype =", device.get("DEVTYPE"),
        "\nnode =", device.device_node,
        "\nsys_path =", device.sys_path,
        "\nsubsystem =", device.subsystem,
        "\nparent =", device.parent,
        "\nID_FS_TYPE =", device.get("ID_FS_TYPE"),
    )

def mount_drive(path_to_device :str):
    try:
        subprocess.run(["sudo", "-n", "./scripts/mountThings.sh", path_to_device, path_to_mount_point], check=True)
        write_debug(f"attempting to mount {path_to_device} to {path_to_mount_point}")
        print(f"attempting to mount {path_to_device} to {path_to_mount_point}")
        return True
    except subprocess.CalledProcessError as e:
        write_debug(f"something went wrong: {e}")
        return False

def umount_drive():
    try:
        subprocess.run(["sudo", "-n", "./scripts/umountThings.sh", path_to_mount_point], check=True)
        write_debug(f"attempting to unmount from {path_to_mount_point}")
        print(f"attempting to unmount from {path_to_mount_point}")
        return True
    except subprocess.CalledProcessError as e:
        write_debug(f"something went wrong: {e}")
        return False


def handle_event(device=None) -> None:
    context = pyudev.Context()

    monitor = pyudev.Monitor.from_netlink(context)

    monitor.filter_by(subsystem='block')
    try:
        for device in iter(monitor.poll, None):
            debug_the_things(device)
            try:
                action = device.action
                path = device.device_node

                if action == "add":
                    write_debug(f"USB storage device added: {path}")
                    print(f"USB storage device added: {path}")
                elif action == "remove":
                    write_debug(f"USB storage device removed: {path}")
                    print(f"USB storage device removed: {path}")
                    umount_drive()
                    write_debug(f"USB storage device unmounted: {path}")
                    print(f"USB storage device unmounted: {path}")
            except (OSError, AttributeError) as e:
                print(f"Error processing device event: {e}")
    except OSError as e:
        print(f"Error monitoring USB storage devices: {e}")

def start() -> threading.Thread:
    thread = threading.Thread(target=handle_event, daemon=False)
    write_debug("usbStorage Detec thread started.")
    print("usbStorage Detec thread started.")
    thread.start()
    return thread
    

def ohShittings():
    print("gay")

if __name__ == "__main__":
    try:
        handle_event(None)
    except KeyboardInterrupt:
        print("Monitoring stopped by user.")
