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
        self.ws_server = None
        self.ser_a = None
        self.ser_b = None
        self.running = False
        self.thread = None

        # Motion parameters
        self.speed = 1.0       # Hz
        self.stroke = 50.0     # % (0-100)
        self.offset = 50.0     # % (0-100)
        self.phase_shift = 180 # Degrees (0 = sync, 180 = alternating)

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

    def _send_cmd(self, ser, cmd):
        if self.ws_server:
            self.ws_server.broadcast(f"{cmd}\n")
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

            # Calculate positions based on sine wave
            # Phase is in radians: 2*pi*f*t
            # Amplitude is stroke/2
            # Offset is center position

            # Normalize inputs
            amp = (self.stroke / 100.0) * 5000 # Amplitude in T-Code units (0-5000)
            center = (self.offset / 100.0) * 10000 # Center in T-Code units (0-10000)

            # Clamp center so stroke doesn't exceed 0-9999
            if center - amp < 0: center = amp
            if center + amp > 9999: center = 9999 - amp

            # Calculate Phase A
            phase_a = 2 * math.pi * self.speed * t
            pos_a = center + amp * math.sin(phase_a)

            # Calculate Phase B (with shift)
            phase_b = phase_a + math.radians(self.phase_shift)
            pos_b = center + amp * math.sin(phase_b)

            # Format T-Code (L0 is main stroke)
            cmd_a = f"L0{int(pos_a):04d} I20" # I20 is interpolation interval ~20ms
            cmd_b = f"L0{int(pos_b):04d} I20"

            self._send_cmd(self.ser_a, cmd_a)
            self._send_cmd(self.ser_b, cmd_b)

            # Update time
            t += dt

            # Maintain loop timing
            elapsed = time.time() - start_time
            sleep_time = max(0, dt - elapsed)
            time.sleep(sleep_time)

        # Center devices on stop
        self._send_cmd(self.ser_a, "L05000 I1000")
        self._send_cmd(self.ser_b, "L05000 I1000")
        logger.info("Motion stopped and devices centered")

class DualOSRGui:
    def __init__(self, root):
        self.root = root
        self.root.title("Dual OSR Footjob Simulator")
        self.root.geometry("600x700")
        self.controller = DualOSRController()

        self.create_widgets()

    def create_widgets(self):
        # --- WebSocket Section ---
        ws_frame = ttk.LabelFrame(self.root, text="WebSocket Server")
        ws_frame.pack(fill="x", padx=10, pady=5)

        row_ws = ttk.Frame(ws_frame)
        row_ws.pack(fill="x", padx=5, pady=2)

        self.enable_ws = tk.BooleanVar(value=True)
        ttk.Checkbutton(row_ws, text="Enable WS Server", variable=self.enable_ws).pack(side="left", padx=5)

        ttk.Label(row_ws, text="Port:").pack(side="left")
        self.ws_port = tk.IntVar(value=8766)
        ttk.Entry(row_ws, textvariable=self.ws_port, width=6).pack(side="left", padx=5)

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

        # Stroke
        ttk.Label(ctrl_frame, text="Stroke Length (%):").pack(anchor="w", padx=5)
        self.stroke_var = tk.DoubleVar(value=50.0)
        self.stroke_scale = ttk.Scale(ctrl_frame, from_=0.0, to=100.0, variable=self.stroke_var, command=self.update_params)
        self.stroke_scale.pack(fill="x", padx=5, pady=2)

        # Offset
        ttk.Label(ctrl_frame, text="Center Offset (%):").pack(anchor="w", padx=5)
        self.offset_var = tk.DoubleVar(value=50.0)
        self.offset_scale = ttk.Scale(ctrl_frame, from_=0.0, to=100.0, variable=self.offset_var, command=self.update_params)
        self.offset_scale.pack(fill="x", padx=5, pady=2)

        # Mode (Sync vs Alternating)
        mode_frame = ttk.Frame(ctrl_frame)
        mode_frame.pack(fill="x", padx=5, pady=10)
        self.mode_var = tk.StringVar(value="alternating")
        ttk.Radiobutton(mode_frame, text="Alternating (Walk)", variable=self.mode_var, value="alternating", command=self.update_params).pack(side="left", padx=10)
        ttk.Radiobutton(mode_frame, text="Sync (Jump)", variable=self.mode_var, value="sync", command=self.update_params).pack(side="left", padx=10)

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
        self.controller.offset = self.offset_var.get()
        if self.mode_var.get() == "sync":
            self.controller.phase_shift = 0
        else:
            self.controller.phase_shift = 180

    def toggle_motion(self):
        if not self.controller.running:
            if self.enable_ws.get():
                if not self.controller.ws_server:
                    self.controller.ws_server = TCodeWSServer(port=self.ws_port.get())
                self.controller.ws_server.start()
            else:
                if self.controller.ws_server:
                    self.controller.ws_server.stop()
                    self.controller.ws_server = None

            self.update_params() # Ensure latest params are set
            self.controller.start_motion()
            self.btn_start.config(text="STOP MOTION")
        else:
            self.controller.stop_motion()
            if self.controller.ws_server:
                self.controller.ws_server.stop()
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
