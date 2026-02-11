# toy-relay: UDP to Serial T-Code Relay

This application bridges the gap between a networked T-Code source and a direct-attached serial device like an OSR. It's the perfect solution for remotely controlling your device.

## Core Use Case

This tool is designed for a specific scenario: you are running a T-Code generating application (like [ToySerialController](https://github.com/Yoooi0/ToySerialController) in Virt-a-Mate) on one machine, but your OSR or other serial toy is physically connected to a *different* machine.

Since the toy itself does not have network capabilities, this relay runs on the machine with the toy attached. It listens for UDP commands from your remote application and forwards them directly to the toy's serial port.

### Architecture

```
   [ Remote PC running VaM ]          [ Local PC with OSR Attached ]
  +-------------------------+        +------------------------------+        +--------------+
  |                         |        |                              |        |              |
  |  [ToySerialController]  |--UDP-->|  [toy-relay]                 |--SERIAL->|  [OSR Device]|
  |    (Sends T-Code)       |        |  (Receives UDP, Forwards)    |        |              |
  |                         |        |                              |        |              |
  +-------------------------+        +------------------------------+        +--------------+
      (Over the Network)                 (USB/Serial Connection)
```

## Features

*   **Remote Control Bridge:** Solves the problem of controlling a non-networked serial device from a remote machine.
*   **Intelligent Command Merging:** Smooths motion by merging rapid T-Code commands, reducing stutter and jitter.
*   **Bidirectional Communication:** Relays feedback from the device (if any) back to the remote application.
*   **Simple GUI:** An easy-to-use interface for setup, connection monitoring, and manual command testing.
*   **Safety Watchdog:** Automatically centers the device if the network signal is lost, preventing runaway motion.
*   **Dummy Mode:** Allows for testing the network connection without a physical device attached.

## Dependencies

*   `pyserial`

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1.  Run the application on the machine that the OSR device is physically connected to.
    ```bash
    python udp_to_serial.py
    ```
2.  In the GUI, select the correct **Serial Port** for your device and set the **Baud Rate**.
3.  Ensure the **UDP Listen** IP address is one that is reachable from your remote machine (e.g., `0.0.0.0` to listen on all interfaces, or the specific IP of the machine).
4.  In your remote application (e.g., ToySerialController), set its UDP output to target the IP address and port of the machine running `toy-relay`.
5.  Click **Start Relay Service**.

### Sending Test Data

The `udp_sender_test.py` script can be used to test if the relay is receiving UDP packets correctly. You can run it from the local or a remote machine.

```bash
python udp_sender_test.py
```
*You may need to edit the `UDP_IP` in the script to match the IP of the machine running the relay.*

## Testing

The project includes unit tests for the core logic. To run them:

```bash
python tests/test_udp_to_serial.py
```
