import tkinter as tk
from tkinter import ttk, scrolledtext
import serial
import serial.tools.list_ports
import threading
import time
import math
import logging

import asyncio
import websockets

class TCodeWSServer:
    def __init__(self, port=8766):
        self.port = port
        self.clients = set()
        self.loop = None
        self.running = False
        self.thread = None

    async def _handler(self, websocket, path=None):
        self.clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)

    def _start_server(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        start_server = websockets.serve(self._handler, "0.0.0.0", self.port)
        self.server = self.loop.run_until_complete(start_server)

        logger.info(f"WebSocket server started on port {self.port}")
        self.loop.run_forever()

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._start_server, daemon=True)
            self.thread.start()

    def stop(self):
        if self.running and self.loop:
            self.running = False
            self.loop.call_soon_threadsafe(self.server.close)
            self.loop.call_soon_threadsafe(self.loop.stop)
            logger.info("WebSocket server stopped")

    def broadcast(self, message):
        if not self.running or not self.clients or not self.loop:
            return

        async def _broadcast():
            if self.clients:
                await asyncio.gather(*[client.send(message) for client in self.clients], return_exceptions=True)

        asyncio.run_coroutine_threadsafe(_broadcast(), self.loop)


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class DualOSRController:
    def __init__(self):
        self.ws_server_a = None
        self.ws_server_b = None
        self.ser_a = None
        self.ser_b = None
        self.running = False
        self.thread = None

        # Motion parameters
        self.speed = 1.0       # Hz
        self.stroke = 50.0     # % (0-100)
        self.offset = 50.0     # % (0-100)
        self.phase_shift = 180 # Degrees (0 = sync, 180 = alternating)

        # New Motion Parameters
        self.pitch_amp = 50.0  # R2
        self.roll_amp = 50.0   # R1
        self.twist_amp = 50.0  # R0
        self.base_squeeze = 50.0 # Base L0 offset
        self.ankle_angle_offset = 50.0 # Base R2 offset
        self.motion_mode = "v_stroke"


        # Device status
        self.connected_a = False
        self.connected_b = False

    def connect_device_a(self, port):
        if self.ser_a and self.ser_a.is_open:
            self.ser_a.close()
        try:
            self.ser_a = serial.Serial(port, 921600, timeout=0.1)
            self.connected_a = True
            logger.info(f"Connected Device A on {port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect Device A: {e}")
            self.connected_a = False
            return False

    def connect_device_b(self, port):
        if self.ser_b and self.ser_b.is_open:
            self.ser_b.close()
        try:
            self.ser_b = serial.Serial(port, 921600, timeout=0.1)
            self.connected_b = True
            logger.info(f"Connected Device B on {port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect Device B: {e}")
            self.connected_b = False
            return False

    def disconnect_all(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join()

        if self.ser_a and self.ser_a.is_open:
            self.ser_a.close()
        if self.ser_b and self.ser_b.is_open:
            self.ser_b.close()
        self.connected_a = False
        self.connected_b = False
        logger.info("All devices disconnected")

    def start_motion(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.motion_loop, daemon=True)
            self.thread.start()
            logger.info("Motion started")

    def stop_motion(self):
        self.running = False
        logger.info("Motion stopping...")

    def _send_cmd(self, ser, cmd, ws_server=None):
        if ws_server:
            ws_server.broadcast(f"{cmd}\n")
        if ser and ser.is_open:
            try:
                ser.write(f"{cmd}\n".encode())
            except Exception:
                pass

    def motion_loop(self):
        t = 0.0
        dt = 0.02 # 50Hz update rate

        while self.running:
            start_time = time.time()

            phase_a = 2 * math.pi * self.speed * t
            phase_b = phase_a + math.radians(self.phase_shift)

            # Amplitudes (0-5000)
            amp_l0 = (self.stroke / 100.0) * 5000
            amp_r2 = (self.pitch_amp / 100.0) * 5000
            amp_r1 = (self.roll_amp / 100.0) * 5000
            amp_r0 = (self.twist_amp / 100.0) * 5000

            # Centers (0-9999)
            center_l0 = (self.base_squeeze / 100.0) * 9999
            center_rx = 5000
            center_r2 = (self.ankle_angle_offset / 100.0) * 9999

            # Clamp L0
            if center_l0 - amp_l0 < 0: center_l0 = amp_l0
            if center_l0 + amp_l0 > 9999: center_l0 = 9999 - amp_l0

            def clamp(val):
                return max(0, min(9999, int(val)))

            cmd_a_parts = []
            cmd_b_parts = []

            if self.motion_mode == "v_stroke":
                # Devices are at 45 deg facing center.
                # L0 pushing out moves feet inwards & forwards.
                # To keep soles parallel to the center axis, pitch (R2) must tilt toes "up" (relative to the device).
                # Assuming R2=9999 is pitch up, and R2=0000 is pitch down.
                pos_l0 = center_l0 + amp_l0 * math.sin(phase_a)

                # Active pitch compensation: when L0 extends (sin -> +1), R2 pitches UP to compensate for the 45deg downward slope.
                # Use pitch_amp to control the *intensity* of this compensation.
                pos_a_r2 = center_r2 + amp_r2 * math.sin(phase_a)
                pos_b_r2 = center_r2 + amp_r2 * math.sin(phase_a) # Symmetric

                cmd_a_parts.extend([f"L0{clamp(pos_l0):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_l0):04d}", f"R2{clamp(pos_b_r2):04d}"])

            elif self.motion_mode == "alternating_step":
                # Left foot pushes in (L0) and points toe down (R2 down, e.g. -R2).
                # Right foot pulls out (L0) and points toe up (R2 up, e.g. +R2).
                pos_a_l0 = center_l0 + amp_l0 * math.sin(phase_a)
                pos_b_l0 = center_l0 + amp_l0 * math.sin(phase_b)

                # When L0 pushes (sin -> +1), R2 pitches down (cos or -sin -> -1).
                # We use -sin so it's in phase with the stroke: push out -> toe down.
                pos_a_r2 = center_r2 - amp_r2 * math.sin(phase_a)
                pos_b_r2 = center_r2 - amp_r2 * math.sin(phase_b)

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"R2{clamp(pos_b_r2):04d}"])

            elif self.motion_mode == "wrapping_twist":
                # Hold a constant close squeeze (L0).
                # Roll soles inwards (R1). Assuming +R1 is roll inwards for left foot, then -R1 is inwards for right foot.
                # (Or vice versa, they should be out of phase to roll symmetrically relative to the center).
                pos_a_r1 = center_rx + amp_r1 * math.sin(phase_a)
                pos_b_r1 = center_rx - amp_r1 * math.sin(phase_a) # Mirror roll inwards

                # Alternate twisting to rub the sides (R0)
                pos_a_r0 = center_rx + amp_r0 * math.cos(phase_a)
                pos_b_r0 = center_rx + amp_r0 * math.cos(phase_b) # Alternating twist

                cmd_a_parts.extend([f"L0{clamp(center_l0):04d}", f"R1{clamp(pos_a_r1):04d}", f"R0{clamp(pos_a_r0):04d}"])
                cmd_b_parts.extend([f"L0{clamp(center_l0):04d}", f"R1{clamp(pos_b_r1):04d}", f"R0{clamp(pos_b_r0):04d}"])

            elif self.motion_mode == "sole_rub":
                pos_a_r2 = center_r2 + amp_r2 * math.sin(phase_a)
                pos_b_r2 = center_r2 + amp_r2 * math.sin(phase_b)

                pos_a_r1 = center_rx + amp_r1 * math.cos(phase_a)
                pos_b_r1 = center_rx + amp_r1 * math.cos(phase_b)

                cmd_a_parts.extend([f"L0{clamp(center_l0):04d}", f"R2{clamp(pos_a_r2):04d}", f"R1{clamp(pos_a_r1):04d}"])
                cmd_b_parts.extend([f"L0{clamp(center_l0):04d}", f"R2{clamp(pos_b_r2):04d}", f"R1{clamp(pos_b_r1):04d}"])

            elif self.motion_mode == "toe_tease":
                # Quick flickering pitch (R2) to tap the toes.
                # L0 remains relatively steady but close.
                # Use a 2x frequency multiplier for a faster "teasing" feel.
                fast_phase_a = phase_a * 2.0
                fast_phase_b = phase_b * 2.0

                # Toes point "down" to tap towards the center
                # Assuming R2 < 5000 is pointing toes down. We sweep between 5000 and (5000 - amp_r2)
                pos_a_r2 = center_r2 - (amp_r2 / 2.0) - (amp_r2 / 2.0) * math.sin(fast_phase_a)
                pos_b_r2 = center_r2 - (amp_r2 / 2.0) - (amp_r2 / 2.0) * math.sin(fast_phase_b)

                # Slight pulsing L0
                pos_l0 = center_l0 + (amp_l0 * 0.1) * math.sin(phase_a)

                cmd_a_parts.extend([f"L0{clamp(pos_l0):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_l0):04d}", f"R2{clamp(pos_b_r2):04d}"])

            elif self.motion_mode == "edge_stroking":
                # Feet roll heavily INWARDS (R1) to create a tight V-groove with the soles touching.
                # Left rolls in (+R1?), Right rolls in (-R1?). We'll hold it steady.
                pos_a_r1 = center_rx + amp_r1
                pos_b_r1 = center_rx - amp_r1

                # L0 synchronously strokes up and down the groove
                pos_l0 = center_l0 + amp_l0 * math.sin(phase_a)

                # Slight pitch to keep the stroke parallel to the target
                pos_r2 = center_r2 + amp_r2 * math.sin(phase_a)

                cmd_a_parts.extend([f"L0{clamp(pos_l0):04d}", f"R1{clamp(pos_a_r1):04d}", f"R2{clamp(pos_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_l0):04d}", f"R1{clamp(pos_b_r1):04d}", f"R2{clamp(pos_r2):04d}"])

            elif self.motion_mode == "heel_press":
                # Toes pitched heavily UP (away from target) to expose the heels.
                # Assuming R2 > 5000 is pitch up.
                pos_r2 = center_r2 + amp_r2

                # Deep, slow squeezing L0
                slow_phase = phase_a * 0.5
                pos_l0 = center_l0 + amp_l0 * math.sin(slow_phase)

                # Twisting (R0) slightly back and forth to grind the heels
                pos_a_r0 = center_rx + amp_r0 * math.cos(slow_phase)
                pos_b_r0 = center_rx - amp_r0 * math.cos(slow_phase)

                cmd_a_parts.extend([f"L0{clamp(pos_l0):04d}", f"R2{clamp(pos_r2):04d}", f"R0{clamp(pos_a_r0):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_l0):04d}", f"R2{clamp(pos_r2):04d}", f"R0{clamp(pos_b_r0):04d}"])

            elif self.motion_mode == "circling_tease":
                # Feet held gently on the target.
                # Roll (R1) and Pitch (R2) move in a circular sine/cosine pattern to create a grinding orbital motion.
                pos_a_r1 = center_rx + amp_r1 * math.sin(phase_a)
                pos_b_r1 = center_rx - amp_r1 * math.sin(phase_a) # mirror roll

                pos_a_r2 = center_r2 + amp_r2 * math.cos(phase_a)
                pos_b_r2 = center_r2 + amp_r2 * math.cos(phase_a) # sync pitch

                cmd_a_parts.extend([f"L0{clamp(center_l0):04d}", f"R1{clamp(pos_a_r1):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(center_l0):04d}", f"R1{clamp(pos_b_r1):04d}", f"R2{clamp(pos_b_r2):04d}"])

            elif self.motion_mode == "single_foot_tease_left":
                # Left foot teases with rapid flickering pitch, Right foot stays still at base squeeze
                fast_phase_a = phase_a * 2.0

                # Active Left (Device A)
                pos_a_r2 = center_r2 - (amp_r2 / 2.0) - (amp_r2 / 2.0) * math.sin(fast_phase_a)
                pos_a_l0 = center_l0 + (amp_l0 * 0.1) * math.sin(phase_a)

                # Static Right (Device B)
                pos_b_r2 = center_r2
                pos_b_l0 = center_l0

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"R2{clamp(pos_b_r2):04d}"])

            elif self.motion_mode == "single_foot_tease_right":
                # Right foot teases with rapid flickering pitch, Left foot stays still at base squeeze
                fast_phase_b = phase_a * 2.0 # phase_a is fine here since it's isolated

                # Static Left (Device A)
                pos_a_r2 = center_r2
                pos_a_l0 = center_l0

                # Active Right (Device B)
                pos_b_r2 = center_r2 - (amp_r2 / 2.0) - (amp_r2 / 2.0) * math.sin(fast_phase_b)
                pos_b_l0 = center_l0 + (amp_l0 * 0.1) * math.sin(phase_a)

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"R2{clamp(pos_b_r2):04d}"])

            elif self.motion_mode == "single_foot_stroke_left":
                # Left foot strokes with pitch compensation, Right foot holds still
                pos_a_l0 = center_l0 + amp_l0 * math.sin(phase_a)
                pos_a_r2 = center_r2 + amp_r2 * math.sin(phase_a)

                pos_b_l0 = center_l0
                pos_b_r2 = center_r2

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"R2{clamp(pos_b_r2):04d}"])

            elif self.motion_mode == "single_foot_stroke_right":
                # Right foot strokes with pitch compensation, Left foot holds still
                pos_a_l0 = center_l0
                pos_a_r2 = center_r2

                pos_b_l0 = center_l0 + amp_l0 * math.sin(phase_a) # Use phase_a for the active foot
                pos_b_r2 = center_r2 + amp_r2 * math.sin(phase_a)

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"R2{clamp(pos_b_r2):04d}"])

            else: # fallback
                pos_a = center_l0 + amp_l0 * math.sin(phase_a)
                pos_b = center_l0 + amp_l0 * math.sin(phase_b)
                cmd_a_parts.append(f"L0{clamp(pos_a):04d}")
                cmd_b_parts.append(f"L0{clamp(pos_b):04d}")

            # Add timing interval
            cmd_a = " ".join(cmd_a_parts) + " I20"
            cmd_b = " ".join(cmd_b_parts) + " I20"

            self._send_cmd(self.ser_a, cmd_a, self.ws_server_a)
            self._send_cmd(self.ser_b, cmd_b, self.ws_server_b)

            # Update time
            t += dt

            # Maintain loop timing
            elapsed = time.time() - start_time
            sleep_time = max(0, dt - elapsed)
            time.sleep(sleep_time)

        # Center devices on stop
        self._send_cmd(self.ser_a, "L05000 I1000", self.ws_server_a)
        self._send_cmd(self.ser_b, "L05000 I1000", self.ws_server_b)
        logger.info("Motion stopped and devices centered")

class DualOSRGui:
    def __init__(self, root):
        self.root = root
        self.root.title("Dual OSR Footjob Simulator")
        self.root.geometry("600x900")
        self.controller = DualOSRController()

        self.create_widgets()

    def create_widgets(self):
        # --- WebSocket Section ---
        ws_frame = ttk.LabelFrame(self.root, text="WebSocket Servers")
        ws_frame.pack(fill="x", padx=10, pady=5)

        row_ws = ttk.Frame(ws_frame)
        row_ws.pack(fill="x", padx=5, pady=2)

        self.enable_ws = tk.BooleanVar(value=True)
        ttk.Checkbutton(row_ws, text="Enable WS Servers", variable=self.enable_ws).pack(side="left", padx=5)

        ttk.Label(row_ws, text="Port A:").pack(side="left", padx=(10, 2))
        self.ws_port_a = tk.IntVar(value=8766)
        ttk.Entry(row_ws, textvariable=self.ws_port_a, width=6).pack(side="left")

        ttk.Label(row_ws, text="Port B:").pack(side="left", padx=(10, 2))
        self.ws_port_b = tk.IntVar(value=8767)
        ttk.Entry(row_ws, textvariable=self.ws_port_b, width=6).pack(side="left")

        # --- Connection Section ---
        conn_frame = ttk.LabelFrame(self.root, text="Connections")
        conn_frame.pack(fill="x", padx=10, pady=5)

        # Device A
        dev_a_frame = ttk.Frame(conn_frame)
        dev_a_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(dev_a_frame, text="Device A (Left):").pack(side="left")
        self.port_a = tk.StringVar()
        self.combo_a = ttk.Combobox(dev_a_frame, textvariable=self.port_a, width=15)
        self.combo_a.pack(side="left", padx=5)
        self.btn_connect_a = ttk.Button(dev_a_frame, text="Connect", command=self.toggle_connect_a)
        self.btn_connect_a.pack(side="left")

        # Device B
        dev_b_frame = ttk.Frame(conn_frame)
        dev_b_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(dev_b_frame, text="Device B (Right):").pack(side="left")
        self.port_b = tk.StringVar()
        self.combo_b = ttk.Combobox(dev_b_frame, textvariable=self.port_b, width=15)
        self.combo_b.pack(side="left", padx=5)
        self.btn_connect_b = ttk.Button(dev_b_frame, text="Connect", command=self.toggle_connect_b)
        self.btn_connect_b.pack(side="left")

        ttk.Button(conn_frame, text="Refresh Ports", command=self.refresh_ports).pack(pady=5)

        # --- Motion Control Section ---
        ctrl_frame = ttk.LabelFrame(self.root, text="Motion Control")
        ctrl_frame.pack(fill="x", padx=10, pady=5)

        # Speed
        ttk.Label(ctrl_frame, text="Speed (Hz):").pack(anchor="w", padx=5)
        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_scale = ttk.Scale(ctrl_frame, from_=0.1, to=5.0, variable=self.speed_var, command=self.update_params)
        self.speed_scale.pack(fill="x", padx=5, pady=2)

        # Mode Selection
        mode_frame = ttk.Frame(ctrl_frame)
        mode_frame.pack(fill="x", padx=5, pady=5)
        ttk.Label(mode_frame, text="Motion Mode:").pack(side="left")
        self.mode_var = tk.StringVar(value="v_stroke")
        modes = [
            "v_stroke", "alternating_step", "wrapping_twist", "sole_rub",
            "toe_tease", "edge_stroking", "heel_press", "circling_tease",
            "single_foot_tease_left", "single_foot_tease_right",
            "single_foot_stroke_left", "single_foot_stroke_right"
        ]
        self.mode_combo = ttk.Combobox(mode_frame, textvariable=self.mode_var, values=modes, state="readonly")
        self.mode_combo.pack(side="left", padx=5)
        self.mode_combo.bind("<<ComboboxSelected>>", self.update_params)

        # Stroke / Base Squeeze (L0)
        ttk.Label(ctrl_frame, text="L0 Stroke Length (%):").pack(anchor="w", padx=5)
        self.stroke_var = tk.DoubleVar(value=50.0)
        self.stroke_scale = ttk.Scale(ctrl_frame, from_=0.0, to=100.0, variable=self.stroke_var, command=self.update_params)
        self.stroke_scale.pack(fill="x", padx=5, pady=2)

        ttk.Label(ctrl_frame, text="L0 Base Squeeze Offset (%):").pack(anchor="w", padx=5)
        self.base_squeeze_var = tk.DoubleVar(value=50.0)
        self.base_squeeze_scale = ttk.Scale(ctrl_frame, from_=0.0, to=100.0, variable=self.base_squeeze_var, command=self.update_params)
        self.base_squeeze_scale.pack(fill="x", padx=5, pady=2)

        # Advanced Axes
        adv_frame = ttk.LabelFrame(ctrl_frame, text="Advanced Axes (Depends on Mode)")
        adv_frame.pack(fill="x", padx=5, pady=5)

        # Ankle Pitch Offset (R2 Base)
        ttk.Label(adv_frame, text="Ankle Pitch Offset R2 Base (%):").pack(anchor="w", padx=5)
        self.ankle_offset_var = tk.DoubleVar(value=50.0)
        self.ankle_scale = ttk.Scale(adv_frame, from_=0.0, to=100.0, variable=self.ankle_offset_var, command=self.update_params)
        self.ankle_scale.pack(fill="x", padx=5, pady=2)

        # Pitch (R2)
        ttk.Label(adv_frame, text="Pitch Amplitude R2 (%):").pack(anchor="w", padx=5)
        self.pitch_amp_var = tk.DoubleVar(value=50.0)
        self.pitch_scale = ttk.Scale(adv_frame, from_=0.0, to=100.0, variable=self.pitch_amp_var, command=self.update_params)
        self.pitch_scale.pack(fill="x", padx=5, pady=2)

        # Roll (R1)
        ttk.Label(adv_frame, text="Roll Amplitude R1 (%):").pack(anchor="w", padx=5)
        self.roll_amp_var = tk.DoubleVar(value=50.0)
        self.roll_scale = ttk.Scale(adv_frame, from_=0.0, to=100.0, variable=self.roll_amp_var, command=self.update_params)
        self.roll_scale.pack(fill="x", padx=5, pady=2)

        # Twist (R0)
        ttk.Label(adv_frame, text="Twist Amplitude R0 (%):").pack(anchor="w", padx=5)
        self.twist_amp_var = tk.DoubleVar(value=50.0)
        self.twist_scale = ttk.Scale(adv_frame, from_=0.0, to=100.0, variable=self.twist_amp_var, command=self.update_params)
        self.twist_scale.pack(fill="x", padx=5, pady=2)

        # Start/Stop
        self.btn_start = ttk.Button(self.root, text="START MOTION", command=self.toggle_motion)
        self.btn_start.pack(fill="x", padx=20, pady=10, ipady=10)

        # --- Log Section ---
        log_frame = ttk.LabelFrame(self.root, text="Log")
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, state='disabled')
        self.log_text.pack(fill="both", expand=True)

        # Setup custom logging handler
        self.log_handler = TextHandler(self.log_text)
        self.log_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S'))
        logger.addHandler(self.log_handler)

        self.refresh_ports()

    def refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.combo_a['values'] = ports
        self.combo_b['values'] = ports
        if ports:
            if not self.port_a.get(): self.combo_a.current(0)
            if not self.port_b.get(): self.combo_b.current(0)

    def toggle_connect_a(self):
        if not self.controller.connected_a:
            if self.controller.connect_device_a(self.port_a.get()):
                self.btn_connect_a.config(text="Disconnect")
        else:
            self.controller.ser_a.close()
            self.controller.connected_a = False
            self.btn_connect_a.config(text="Connect")
            logger.info("Device A disconnected")

    def toggle_connect_b(self):
        if not self.controller.connected_b:
            if self.controller.connect_device_b(self.port_b.get()):
                self.btn_connect_b.config(text="Disconnect")
        else:
            self.controller.ser_b.close()
            self.controller.connected_b = False
            self.btn_connect_b.config(text="Connect")
            logger.info("Device B disconnected")

    def update_params(self, _=None):
        self.controller.speed = self.speed_var.get()
        self.controller.stroke = self.stroke_var.get()
        self.controller.base_squeeze = self.base_squeeze_var.get()
        self.controller.ankle_angle_offset = self.ankle_offset_var.get()
        self.controller.pitch_amp = self.pitch_amp_var.get()
        self.controller.roll_amp = self.roll_amp_var.get()
        self.controller.twist_amp = self.twist_amp_var.get()

        mode = self.mode_var.get()
        self.controller.motion_mode = mode

        # In some modes, we want synchronous base loops
        if mode in ["v_stroke", "wrapping_twist", "sole_rub", "edge_stroking", "heel_press", "circling_tease", "toe_tease",
                    "single_foot_tease_left", "single_foot_tease_right", "single_foot_stroke_left", "single_foot_stroke_right"]:
            self.controller.phase_shift = 0   # Base phase sync (modes handle mirroring internally if needed)
        else:
            self.controller.phase_shift = 180 # Base phase alternating (e.g. alternating_step)

    def toggle_motion(self):
        if not self.controller.running:
            if self.enable_ws.get():
                if not self.controller.ws_server_a:
                    self.controller.ws_server_a = TCodeWSServer(port=self.ws_port_a.get())
                if not self.controller.ws_server_b:
                    self.controller.ws_server_b = TCodeWSServer(port=self.ws_port_b.get())
                self.controller.ws_server_a.start()
                self.controller.ws_server_b.start()
            else:
                if self.controller.ws_server_a:
                    self.controller.ws_server_a.stop()
                    self.controller.ws_server_a = None
                if self.controller.ws_server_b:
                    self.controller.ws_server_b.stop()
                    self.controller.ws_server_b = None

            self.update_params() # Ensure latest params are set
            self.controller.start_motion()
            self.btn_start.config(text="STOP MOTION")
        else:
            self.controller.stop_motion()
            if self.controller.ws_server_a:
                self.controller.ws_server_a.stop()
            if self.controller.ws_server_b:
                self.controller.ws_server_b.stop()
            self.btn_start.config(text="START MOTION")

class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, msg + "\n")
            self.text_widget.see(tk.END)
            self.text_widget.configure(state='disabled')
        self.text_widget.after(0, append)

if __name__ == "__main__":
    root = tk.Tk()
    app = DualOSRGui(root)
    root.mainloop()
