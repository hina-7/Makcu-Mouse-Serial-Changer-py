import argparse
import ctypes
import random
import string
import sys
import time
from typing import Optional

try:
    from makcu import create_controller
except ImportError:
    create_controller = None


CHARSET = string.digits + string.ascii_uppercase
MIN_SERIAL_LENGTH = 8
MAX_SERIAL_LENGTH = 11


class LogitechSerialType:
    DEVICE = "device"
    BOX = "box"


def set_console_title(title: str) -> None:
    if sys.platform != "win32":
        return

    try:
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    except Exception:
        pass


def clamp_serial_length(length: int) -> int:
    return max(MIN_SERIAL_LENGTH, min(MAX_SERIAL_LENGTH, length))


def random_serial(
    length: int = 10,
    serial_type: str = LogitechSerialType.DEVICE,
) -> str:
    length = clamp_serial_length(length)
    suffix = "9" if serial_type == LogitechSerialType.BOX else "8"
    body = "".join(random.choice(CHARSET) for _ in range(length - 1))
    return body + suffix


def init_makcu(port: str = "", debug: bool = False):
    if create_controller is None:
        print("\n (!) Python package 'makcu' is not installed.")
        print(" (!) Install it with: pip install makcu")
        return None

    try:
        controller = create_controller(
            fallback_com_port=port,
            debug=debug,
            auto_reconnect=True,
            override_port=bool(port),
        )
    except TypeError:
        controller = create_controller(port, debug=debug)
    except Exception as exc:
        print("\n (!) Makcu is not connected or failed to initialize.")
        print(f" (!) {exc}")
        return None

    try:
        if not controller.is_connected():
            print("\n (!) Failed to connect to your makcu.")
            return None
    except Exception as exc:
        print("\n (!) Failed to check makcu connection.")
        print(f" (!) {exc}")
        return None

    try:
        if hasattr(controller, "set_button_callback"):
            controller.set_button_callback(None)
    except Exception:
        pass

    print("\n (+) Makcu initialized.")
    return controller


def get_mouse_serial(controller) -> str:
    if not hasattr(controller, "transport"):
        return ""

    try:
        response = controller.transport.send_command(
            "km.serial()",
            expect_response=True,
            timeout=0.1,
        )
    except TypeError:
        response = controller.transport.send_command("km.serial()", True, 0.1)
    except Exception:
        return ""

    return (response or "").strip()


def set_mouse_serial(controller, serial: str) -> bool:
    try:
        controller.spoof_serial(serial)
        return True
    except Exception as exc:
        print(f"\n (!) Failed to send serial command: {exc}")
        return False


def reset_mouse_serial(controller) -> bool:
    try:
        controller.reset_serial()
        return True
    except Exception as exc:
        print(f"\n (!) Failed to send reset command: {exc}")
        return False


def parse_length(raw: str) -> Optional[int]:
    try:
        return int(raw.strip())
    except ValueError:
        return None


def prompt_length() -> int:
    while True:
        print(
            "\n (.) Type the desired serial length. BETWEEN 8-11, "
            "TYPE 0 TO RESET THE SERIAL"
        )
        raw = input(" (.) length: ")
        length = parse_length(raw)

        if length is None:
            print("\n (!) Please type a number.")
            continue

        if length == 0 or MIN_SERIAL_LENGTH <= length <= MAX_SERIAL_LENGTH:
            return length

        print("\n (!) Invalid length. Use 8-11, or 0 to reset.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Makcu Mouse Serial Changer Python remake."
    )
    parser.add_argument("--port", default="", help="Force a COM port, e.g. COM3.")
    parser.add_argument("--debug", action="store_true", help="Enable makcu debug logs.")
    parser.add_argument(
        "--length",
        type=int,
        help="Generate and apply a random serial with this length (8-11).",
    )
    parser.add_argument("--serial", help="Apply this exact serial instead of generating.")
    parser.add_argument("--reset", action="store_true", help="Reset serial and exit.")
    parser.add_argument(
        "--box",
        action="store_true",
        help="Generate a box serial ending with 9 instead of device serial ending with 8.",
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Do not wait before exiting.",
    )
    return parser.parse_args()


def disconnect(controller) -> None:
    try:
        controller.disconnect()
    except Exception:
        pass


def wait_before_exit(enabled: bool) -> None:
    if enabled:
        time.sleep(3)


def main() -> int:
    args = parse_args()
    set_console_title("Makcu Mouse Serial Changer. Made With <3 by Mhatt")

    controller = init_makcu(port=args.port, debug=args.debug)
    if controller is None:
        wait_before_exit(not args.no_wait)
        return 1

    try:
        current_serial = get_mouse_serial(controller)
        print(f"\n (-) Current Mouse Serial: {current_serial}")

        if args.reset:
            length = 0
        elif args.serial:
            length = len(args.serial)
        elif args.length is not None:
            length = args.length
        else:
            length = prompt_length()

        if length == 0:
            if reset_mouse_serial(controller):
                print("\n (+) Successfully resetted your mouse serial <3")
            else:
                print("\n (!) Failed to reset the mouse serial.")

            return 0

        if not MIN_SERIAL_LENGTH <= length <= MAX_SERIAL_LENGTH:
            print("\n (!) Invalid serial length. Use 8-11, or 0 to reset.")
            return 1

        if args.serial:
            new_serial = args.serial.strip().upper()
        else:
            serial_type = LogitechSerialType.BOX if args.box else LogitechSerialType.DEVICE
            new_serial = random_serial(length, serial_type)

        print(f"\n ciao: {new_serial}")
        sent = set_mouse_serial(controller, new_serial)

        time.sleep(0.2)
        confirmed_serial = get_mouse_serial(controller)

        if not sent or not confirmed_serial or confirmed_serial == current_serial:
            print("\n (!) Failed to set the mouse serial.")
            if confirmed_serial:
                print(f" (-) Readback Mouse Serial: {confirmed_serial}")
            return 1

        print("\n (+) Successfully changed your mouse serial <3")
        print(f" (-) New Mouse Serial: {confirmed_serial}")
        return 0
    finally:
        disconnect(controller)
        print("\n (x) Exiting...")
        wait_before_exit(not args.no_wait)


if __name__ == "__main__":
    raise SystemExit(main())
