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
        self.motion_mode = "walk"


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

            # Clamp L0
            if center_l0 - amp_l0 < 0: center_l0 = amp_l0
            if center_l0 + amp_l0 > 9999: center_l0 = 9999 - amp_l0

            cmd_a_parts = []
            cmd_b_parts = []

            if self.motion_mode == "walk":
                pos_a = center_l0 + amp_l0 * math.sin(phase_a)
                pos_b = center_l0 + amp_l0 * math.sin(phase_b)
                cmd_a_parts.append(f"L0{int(pos_a):04d}")
                cmd_b_parts.append(f"L0{int(pos_b):04d}")

            elif self.motion_mode == "squeeze_rub":
                # Sync L0 squeeze, alternating R2 pitch
                pos_l0 = center_l0 + amp_l0 * math.sin(phase_a)
                pos_a_r2 = center_rx + amp_r2 * math.sin(phase_a)
                pos_b_r2 = center_rx + amp_r2 * math.sin(phase_b)

                cmd_a_parts.extend([f"L0{int(pos_l0):04d}", f"R2{int(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{int(pos_l0):04d}", f"R2{int(pos_b_r2):04d}"])

            elif self.motion_mode == "ankle_massage":
                # Hold L0 squeeze, alternating R1 roll
                pos_a_r1 = center_rx + amp_r1 * math.sin(phase_a)
                pos_b_r1 = center_rx + amp_r1 * math.sin(phase_b)

                cmd_a_parts.extend([f"L0{int(center_l0):04d}", f"R1{int(pos_a_r1):04d}"])
                cmd_b_parts.extend([f"L0{int(center_l0):04d}", f"R1{int(pos_b_r1):04d}"])

            elif self.motion_mode == "stepping":
                # Alternating L0 and Alternating R2 (pitching down while stepping)
                pos_a_l0 = center_l0 + amp_l0 * math.sin(phase_a)
                pos_b_l0 = center_l0 + amp_l0 * math.sin(phase_b)

                # Pitch correlates with stroke (toe points down when pushing out)
                pos_a_r2 = center_rx + amp_r2 * math.cos(phase_a)
                pos_b_r2 = center_rx + amp_r2 * math.cos(phase_b)

                cmd_a_parts.extend([f"L0{int(pos_a_l0):04d}", f"R2{int(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{int(pos_b_l0):04d}", f"R2{int(pos_b_r2):04d}"])

            elif self.motion_mode == "twisting":
                # Alternating R0 twist and R1 roll, gentle L0 sync
                pos_l0 = center_l0 + (amp_l0 * 0.5) * math.sin(phase_a)

                pos_a_r0 = center_rx + amp_r0 * math.sin(phase_a)
                pos_b_r0 = center_rx + amp_r0 * math.sin(phase_b)

                pos_a_r1 = center_rx + amp_r1 * math.cos(phase_a)
                pos_b_r1 = center_rx + amp_r1 * math.cos(phase_b)

                cmd_a_parts.extend([f"L0{int(pos_l0):04d}", f"R0{int(pos_a_r0):04d}", f"R1{int(pos_a_r1):04d}"])
                cmd_b_parts.extend([f"L0{int(pos_l0):04d}", f"R0{int(pos_b_r0):04d}", f"R1{int(pos_b_r1):04d}"])

            else:
                pos_a = center_l0 + amp_l0 * math.sin(phase_a)
                pos_b = center_l0 + amp_l0 * math.sin(phase_b)
                cmd_a_parts.append(f"L0{int(pos_a):04d}")
                cmd_b_parts.append(f"L0{int(pos_b):04d}")

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
        self.root.geometry("600x850")
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
        self.mode_var = tk.StringVar(value="walk")
        modes = ["walk", "squeeze_rub", "ankle_massage", "stepping", "twisting"]
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
        self.controller.pitch_amp = self.pitch_amp_var.get()
        self.controller.roll_amp = self.roll_amp_var.get()
        self.controller.twist_amp = self.twist_amp_var.get()

        mode = self.mode_var.get()
        self.controller.motion_mode = mode

        # In twisting or squeeze mode, they often operate in sync or have specialized phase handling
        if mode == "squeeze_rub":
            self.controller.phase_shift = 0  # Sync L0
        else:
            self.controller.phase_shift = 180 # Alternating L0

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
