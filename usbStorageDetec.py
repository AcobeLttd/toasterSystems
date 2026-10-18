import queue
import threading
import pyudev

udev_version :int = pyudev.udev_version()
print("udev version:", udev_version)

def debug_the_things(device):
    print(
        "\naction =", device.action,
        "\ntype =", device.get("DEVTYPE"),
        "\nnode =", device.device_node,
        "\nsys_path =", device.sys_path,
        "\nsubsystem =", device.subsystem,
        "\nparent =", device.parent,
        "\nID_FS_TYPE =", device.get("ID_FS_TYPE"),
    )

# def check_if_partiton(device):


def handle_event(device):
    context = pyudev.Context()

    monitor = pyudev.Monitor.from_netlink(context)

    monitor.filter_by(subsystem='block')
    try:
        for device in iter(monitor.poll, None):
            debug_the_things(device)
            try:
                if device.get("DEVTYPE") != "partition":
                    print("oh shittings theres no partition!")
                    continue
                elif device.get("DEVTYPE") == "disk":
                    print("oh shittings theres a disk!")
                    continue

                usb_device = device.find_parent("usb", "usb_device")
                if usb_device is None: 
                    print("oh shittings theres no usb device!")
                    continue

                action = device.action
                path = device.device_node

                if action == "add":
                    print(f"USB storage device added: {path}")
                elif action == "remove":
                    print(f"USB storage device removed: {path}")
            except (OSError, AttributeError) as e:
                print(f"Error processing device event: {e}")
    except OSError as e:
        print(f"Error monitoring USB storage devices: {e}")
    

def ohShittings():
    print("gay")

if __name__ == "__main__":
    try:
        handle_event(None)
    except KeyboardInterrupt:
        print("Monitoring stopped by user.")
