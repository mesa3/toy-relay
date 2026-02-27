import time
import threading
import argparse
import re
import sys
import math

try:
    from ursina import *
    from ursina.prefabs.first_person_controller import FirstPersonController
except ImportError:
    print("Error: 'ursina' module not found. Please install it: pip install ursina")
    sys.exit(1)

try:
    import serial
except ImportError:
    print("Error: 'pyserial' module not found. Please install it: pip install pyserial")
    sys.exit(1)

# --- Configuration ---
DEFAULT_BAUD = 115200

# T-Code Regex: L0, L1, L2 followed by 1-4 digits
# We only care about L0 (Stroke) usually for main movement,
# but let's support parsing any axis.
TCODE_REGEX = re.compile(r'([LR][0-9])(\d+)')

class SerialReader(threading.Thread):
    def __init__(self, port, baudrate=DEFAULT_BAUD, mock=False, mock_speed=1.0, mock_offset=0.0):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.mock = mock
        self.mock_speed = mock_speed
        self.mock_offset = mock_offset
        self.daemon = True
        self.running = False
        self.ser = None

        # Shared state (0.0 to 1.0)
        self.target_position = 0.5
        self.last_update = time.time()

    def run(self):
        self.running = True
        if self.mock:
            self._run_mock()
        else:
            self._run_serial()

    def _run_mock(self):
        print(f"Starting MOCK reader for {self.port}")
        t = 0
        while self.running:
            # Simulate a sine wave movement
            t = time.time() * self.mock_speed + self.mock_offset
            # Map sine (-1 to 1) to (0 to 1)
            val = (math.sin(t) + 1) / 2
            self.target_position = val
            time.sleep(0.01)

    def _run_serial(self):
        print(f"Attempting to open {self.port}...")
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"Connected to {self.port}")
        except Exception as e:
            print(f"Failed to connect to {self.port}: {e}")
            self.running = False
            return

        while self.running and self.ser.is_open:
            try:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    self._parse_tcode(line)
            except Exception as e:
                print(f"Serial error on {self.port}: {e}")
                break

        if self.ser and self.ser.is_open:
            self.ser.close()
        print(f"Disconnected from {self.port}")

    def _parse_tcode(self, line):
        # Example: L05000 I100
        # We look for L0 followed by digits.
        # Normalize 0-9999 to 0.0-1.0
        matches = TCODE_REGEX.findall(line.upper())
        for axis, val_str in matches:
            if axis == 'L0': # Main stroke axis
                try:
                    val = int(val_str)
                    # Clamp 0-9999
                    val = max(0, min(9999, val))
                    self.target_position = val / 9999.0
                    self.last_update = time.time()
                except ValueError:
                    pass

    def stop(self):
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()


def update():
    # Helper to smooth movement
    # Lerp factor
    smooth_speed = 10 * time.dt

    # Update Left Foot
    if left_reader:
        target_y = left_reader.target_position * 4 # Scale height
        left_foot.y = lerp(left_foot.y, target_y, smooth_speed)

        # Color feedback based on position
        left_foot.color = color.lerp(color.azure, color.orange, left_reader.target_position)

    # Update Right Foot
    if right_reader:
        target_y = right_reader.target_position * 4 # Scale height
        right_foot.y = lerp(right_foot.y, target_y, smooth_speed)

        right_foot.color = color.lerp(color.azure, color.orange, right_reader.target_position)


def connect_devices():
    global left_reader, right_reader

    p1 = port_input_1.text
    p2 = port_input_2.text

    if not p1 or not p2:
        print_on_screen("Please enter both COM ports", origin=(0,0), scale=2, duration=2)
        return

    # Stop existing
    if left_reader: left_reader.stop()
    if right_reader: right_reader.stop()

    # Start new
    # Check if "MOCK" is typed to force mock mode
    mock_1 = (p1.upper() == "MOCK")
    mock_2 = (p2.upper() == "MOCK")

    left_reader = SerialReader(port=p1, mock=mock_1, mock_speed=2.0, mock_offset=0.0)
    right_reader = SerialReader(port=p2, mock=mock_2, mock_speed=2.0, mock_offset=3.14) # Pi offset for phase shift

    left_reader.start()
    right_reader.start()

    connect_btn.disabled = True
    connect_btn.text = "Connected"
    connect_btn.color = color.green

# --- Main Application ---

app = Ursina()

window.title = "Dual OSR 3D Visualizer"
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False
window.fps_counter.enabled = True

# Camera
camera.position = (0, 3, -10)
camera.rotation_x = 20

# Light
PointLight(parent=camera, position=(0,0,0))
AmbientLight(color=color.rgba(100, 100, 100, 0.1))

# Scene - Floor
ground = Entity(model='plane', scale=(20, 1, 20), color=color.gray, texture='white_cube', texture_scale=(20,20))

# Feet
# Left Foot
left_foot_anchor = Entity(position=(-2, 0, 0))
left_foot = Entity(parent=left_foot_anchor, model='cube', scale=(1, 1, 2.5), color=color.azure, position=(0,0,0))
Text(text="Left Foot", parent=left_foot_anchor, position=(0, -0.5, -1.5), scale=2, origin=(0,0), color=color.black)

# Right Foot
right_foot_anchor = Entity(position=(2, 0, 0))
right_foot = Entity(parent=right_foot_anchor, model='cube', scale=(1, 1, 2.5), color=color.azure, position=(0,0,0))
Text(text="Right Foot", parent=right_foot_anchor, position=(0, -0.5, -1.5), scale=2, origin=(0,0), color=color.black)

# Visual Rails (Reference lines)
Entity(parent=left_foot_anchor, model='cube', scale=(0.1, 4, 0.1), position=(0, 2, 0), color=color.rgba(0,0,0,0.2))
Entity(parent=right_foot_anchor, model='cube', scale=(0.1, 4, 0.1), position=(0, 2, 0), color=color.rgba(0,0,0,0.2))


# UI
ui_panel = WindowPanel(
    title='Connection Setup',
    content=(
        Text('Left Port (e.g. COM3):'),
        InputField(name='port_1', default_value='MOCK'),
        Text('Right Port (e.g. COM4):'),
        InputField(name='port_2', default_value='MOCK'),
        Button(text='Connect', color=color.azure, on_click=connect_devices),
        Text('Note: Type "MOCK" to simulate movement without hardware.', scale=0.75, color=color.gray)
    ),
    position=(-.7, .4), # Top Left
    scale=(1.5, 1.5) # Scale up UI
)

# Access UI elements via content list
port_input_1 = ui_panel.content[1]
port_input_2 = ui_panel.content[3]
connect_btn = ui_panel.content[4]

# Global Readers
left_reader = None
right_reader = None


if __name__ == '__main__':
    # Parse args for auto-connect (optional)
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", help="Serial port for left device")
    parser.add_argument("--right", help="Serial port for right device")
    args = parser.parse_args()

    if args.left:
        port_input_1.text = args.left
    if args.right:
        port_input_2.text = args.right

    app.run()
