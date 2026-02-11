# UDP to Serial Relay

A Python application that acts as a relay between UDP packets and a serial device. It includes a graphical user interface (GUI) for easy configuration and monitoring. The relay is designed to handle T-Code commands, with intelligent merging of commands for multiple axes.

## Features

*   Forwards UDP packets to a serial port.
*   Receives feedback from the serial port and sends it back to the last UDP client.
*   Intelligently merges T-Code commands received in a short period.
*   GUI for configuration, monitoring, and manual command sending.
*   Dummy mode for testing without a serial device.
*   Safety watchdog to center the device if no signal is received.

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

Then, configure the UDP listening IP/port, select the correct serial port and baud rate, and click "启动中继服务" (Start Relay Service).

### Sending Data

The `udp_sender_test.py` script provides an example of how to send T-Code commands to the relay via UDP.

```bash
python udp_sender_test.py
```

This will send a series of commands to the default address `127.0.0.1:8000`.

## Testing

The project includes a suite of unit tests to verify the core logic, such as T-Code command merging.

To run the tests:

```bash
python test_udp_to_serial.py
```
