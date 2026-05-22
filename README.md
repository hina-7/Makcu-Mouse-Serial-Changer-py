# Makcu Mouse Serial Changer Python

## Overview

Makcu Mouse Serial Changer Python is a lightweight Windows console application written in Python.
It connects to a Makcu device using the `makcu` Python package and allows you to:

- Read the current mouse serial
- Generate a new random serial, 8-11 characters
- Apply a new serial to the device
- Reset the serial to its default value

This project is intended for educational and research purposes.

---

## Features

- Random uppercase alphanumeric serial generation
- Configurable serial length, 8-11 characters
- Enforced ending convention:
  - `8` -> Device serial
  - `9` -> Box serial
- Serial reset support
- Simple command-line interface
- Optional COM port override
- Minimal code, using `pip install makcu`

---

## Dependencies

- Windows OS
- Python 3.10 or newer
- Makcu device
- `makcu` Python package

Install the dependency:

```powershell
pip install makcu
```

---

## Project Structure

```text
MAKCU-SPF/
|
├── main.py
└── README.md
```

---

## How It Works

### 1. Device Initialization

The application:

- Creates a Makcu controller with `makcu.create_controller()`
- Connects to the detected Makcu device
- Optionally uses a manually specified COM port
- Exits safely if no device can be initialized

### 2. Serial Generation

Serials are generated using:

- Python's `random` module
- Uppercase alphanumeric character set
- Configurable length between 8 and 11 characters
- Forced ending digit rule

Example generated serial:

```text
A7XK29LMQ8
```

### 3. Serial Update Process

The program:

1. Retrieves the current serial with `km.serial()`
2. Prompts the user for the desired length
3. Generates a new serial, or resets if `0` is entered
4. Applies the serial with `controller.spoof_serial()`
5. Verifies the change by reading the serial again
6. Displays the result

---

## Usage

Run the script

When prompted:

```text
Type the desired serial length (8-11)
Type 0 to reset the serial
```

Example flow:

```text
(-) Current Mouse Serial: ABCD12348

(.) length: 10

(+) Successfully changed your mouse serial <3
(-) New Mouse Serial: ZYXW987658
```

---

## Command-Line Options

Generate a random 10-character device serial:

```powershell
C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\python.exe MAKCU-SPF\main.py --length 10
```

Generate a box serial ending in `9`:

```powershell
C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\python.exe MAKCU-SPF\main.py --length 10 --box
```

Apply an exact serial:

```powershell
C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\python.exe MAKCU-SPF\main.py --serial ABCD123458
```

Reset the serial:

```powershell
C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\python.exe MAKCU-SPF\main.py --reset
```

Force a COM port:

```powershell
C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\python.exe MAKCU-SPF\main.py --port COM3 --length 10
```

Show all options:

```powershell
C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\python.exe MAKCU-SPF\main.py --help
```

---

## Technical Notes

- Uses the `makcu` Python package instead of `makcu-cpp`
- Uses `controller.spoof_serial(serial)` to apply a serial
- Uses `controller.reset_serial()` to reset the serial
- Reads the serial through the underlying transport command `km.serial()`
- Prevents invalid serial lengths
- Includes basic runtime validation

---

## Disclaimer

This software is provided for educational and research purposes only.

Modifying hardware identifiers may violate manufacturer policies, platform rules, or local regulations.
The author assumes no responsibility for misuse or any resulting consequences.

Use responsibly and at your own risk.

---

## License

MIT License

You are free to use, modify, and distribute this software under the terms of the MIT License.
