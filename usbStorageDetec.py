import queue
import threading
import pyudev

udev_version :int = pyudev.udev_version()
print("udev version:", udev_version)


def handle_event(device):
    context = pyudev.Context()

    monitor = pyudev.Monitor.from_netlink(context)

    monitor.filter_by(subsystem='block')
    for device in iter(monitor.poll, None):
        if device.get("DEVTYPE") != "disk":
            print("oh shittings theres no diski!")
            return 

        usb_device = device.find_parent("usb", "usb_device")
        if usb_device is None: 
            print("oh shittings theres no usb device!")
            return 

        action = device.action
        path = device.device_node

        if action == "add":
            print(f"USB storage device added: {path}")
        elif action == "remove":
            print(f"USB storage device removed: {path}")
    

def ohShittings():
    print("gay")

if __name__ == "__main__":
    handle_event(None)
