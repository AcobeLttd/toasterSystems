import queue
import threading
import pyudev

udev_version :int = pyudev.udev_version()
print("udev version:", udev_version)


def handle_event(device):
    context = pyudev.Context()

    monitor = pyudev.Monitor.from_netlink(context)

    monitor.filter_by(subsystem='block')
    try:
        for device in iter(monitor.poll, None):
            print(
                "action =", device.action,
                "\ntype =", device.get("DEVTYPE"),
                "\nnode =", device.device_node,
                "\nsys_path =", device.sys_path,
            )
            try:
                if device.get("DEVTYPE") != "partition":
                    print("oh shittings theres no partition!")
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
