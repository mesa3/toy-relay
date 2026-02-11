# UDP to Serial Relay for T-Code

This Python application acts as a relay, or bridge, between a UDP T-Code source and a serial device. It is designed to work with applications like [ToySerialController](https://github.com/Yoooi0/ToySerialController) for Virt-a-Mate, which can send motor control commands (T-Code) over a network.

This relay receives those UDP packets, intelligently merges commands to prevent stuttering, and forwards them to a connected serial device, while also relaying feedback from the device back to the sender. It includes a graphical user interface (GUI) for easy configuration and monitoring.

## Features

*   **Bridge for ToySerialController:** Specifically designed to forward T-Code from UDP to a serial port.
*   **Command Merging:** Intelligently merges multiple T-Code commands received in a short period to ensure smooth motion.
*   **Bidirectional Communication:** Receives feedback from the serial port and sends it back to the last UDP client.
*   **GUI:** Easy-to-use interface for configuration, monitoring, and sending manual commands.
*   **Dummy Mode:** Allows for testing the UDP reception without a physical serial device connected.
*   **Safety Watchdog:** Automatically centers the device if the UDP signal is lost for a few seconds.

## Dependencies

*   `pyserial`

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### GUI Mode

To run the application with its graphical interface:

```bash
python udp_to_serial.py
```

Then, configure the UDP listening IP/port (matching the output of your T-Code application), select the correct serial port and baud rate for your device, and click "启动中继服务" (Start Relay Service).

### Sending Test Data

The `udp_sender_test.py` script provides an example of how to send T-Code commands to the relay via UDP for testing purposes.

```bash
python udp_sender_test.py
```

This will send a series of commands to the default address `127.0.0.1:8000`.

## Testing

The project includes a suite of unit tests to verify the core logic, such as T-Code command merging.

To run the tests:

```bash
python tests/test_udp_to_serial.py
```
