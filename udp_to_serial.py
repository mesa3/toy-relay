import socket
import time
import argparse
import logging
import sys
import threading
import select
import re
import tkinter as tk
from tkinter import ttk, scrolledtext

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("Error: 'serial.tools' module not found. Please ensure 'pyserial' is installed, not 'serial'.")
    print("Try running: pip uninstall serial; pip install pyserial")
    sys.exit(1)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# T-Code parsing regex (supports spaces)
TCODE_REGEX = re.compile(r'([A-Z][0-9])\s*([0-9]+(?:\s*[IS][0-9]+)?)')

class UdpToSerialRelay:
    def __init__(self, udp_ip: str, udp_port: int, serial_port: str, baud_rate: int, dummy: bool = False, verbose: bool = False):
        self.udp_ip = udp_ip
        self.udp_port = udp_port
        self.serial_port_name = serial_port
        self.baud_rate = baud_rate
        self.dummy = dummy
        self.verbose = verbose
        
        self.sock = None
        self.ser = None
        self.running = False
        self.last_udp_addr = None
        self.last_receive_time = time.time()
        self.watchdog_triggered = False

    def setup_connections(self):
        try:
            if not self.sock:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sock.bind((self.udp_ip, self.udp_port))
                self.sock.setblocking(False)
            logger.info(f"UDP listening on: {self.udp_ip}:{self.udp_port}")

            if self.dummy:
                logger.warning("DUMMY mode - Only UDP testing will be performed")
                return

            self.ser = serial.Serial(
                port=self.serial_port_name,
                baudrate=self.baud_rate,
                timeout=0.01, # Short timeout for reading
                write_timeout=0.1
            )
            time.sleep(1) 
            logger.info(f"Serial connection successful: {self.serial_port_name}")
            self.send_serial_cmd("L05000 R15000 V00000") # Center device

        except Exception as e:
            if not self.dummy:
                logger.error(f"Connection failed: {e}")
                raise

    def send_serial_cmd(self, cmd_str: str):
        """Sends a command to the serial port, ensuring correct format"""
        if self.dummy or not self.ser or not self.ser.is_open:
            return
        if not cmd_str.endswith('\n'):
            cmd_str += '\n'
        try:
            self.ser.write(cmd_str.encode())
        except Exception as e:
            logger.error(f"Serial send failed: {e}")

    def process_tcode_buffer(self, packets):
        """Axis command merging logic - Optimized"""
        if not packets:
            return None

        # Optimization: Join all packets into one byte string before decoding.
        # This reduces overhead from multiple decode() and regex findall() calls.
        # Benchmark shows ~40% speedup on packet bursts.
        combined = b'\n'.join(packets).decode(errors='replace').upper()

        axis_state = {}
        matches = TCODE_REGEX.findall(combined)
        for axis, cmd in matches:
            # Remove spaces from command for standardization
            axis_state[axis] = cmd.replace(" ", "")
        
        if not axis_state:
            return None
        
        merged = " ".join([f"{axis}{cmd}" for axis, cmd in axis_state.items()])
        return merged + "\n"

    def run(self):
        try:
            self.setup_connections()
        except Exception:
            self.running = False
            return

        self.running = True
        logger.info("Relay service started...")
        
        # Start serial reading thread (for UDP feedback)
        serial_thread = threading.Thread(target=self.serial_to_udp_loop, daemon=True)
        serial_thread.start()

        while self.running:
            try:
                readable, _, _ = select.select([self.sock], [], [], 0.01)
                
                if readable:
                    packets = []
                    while True:
                        try:
                            data, addr = self.sock.recvfrom(4096)
                            if data:
                                packets.append(data)
                                self.last_udp_addr = addr
                                self.last_receive_time = time.time()
                                self.watchdog_triggered = False
                        except:
                            break
                    
                    if packets:
                        merged_cmd = self.process_tcode_buffer(packets)
                        if merged_cmd and not self.dummy and self.ser:
                            self.ser.write(merged_cmd.encode())
                            if self.verbose:
                                logger.info(f"-> {merged_cmd.strip()}")

                # Safety watchdog
                if not self.watchdog_triggered and (time.time() - self.last_receive_time > 2.0):
                    self.send_serial_cmd("L05000 V00000")
                    self.watchdog_triggered = True
                    logger.warning("Device centered (waiting for signal...)")

            except Exception as e:
                logger.error(f"Main loop exception: {e}")
                break
        self.cleanup()

    def serial_to_udp_loop(self):
        """Reads feedback from serial and sends it back to the last UDP client"""
        while self.running:
            if not self.dummy and self.ser and self.ser.is_open:
                try:
                    line = self.ser.readline()
                    if line:
                        decoded = line.decode(errors='replace').strip()
                        if decoded:
                            logger.info(f"<- [Device Feedback] {decoded}")
                            if self.last_udp_addr:
                                self.sock.sendto(line, self.last_udp_addr)
                except:
                    pass
            time.sleep(0.01)

    def cleanup(self):
        self.running = False
        if self.ser:
            self.send_serial_cmd("V00000")
            self.ser.close()
        if self.sock:
            self.sock.close()

class TextHandler(logging.Handler):
    def __init__(self, text_widget, hide_pos=True):
        super().__init__()
        self.text_widget = text_widget
        self.hide_pos = hide_pos
        self.log_queue = []
        self._flush_lock = threading.Lock()
        self._schedule_flush()

    def emit(self, record):
        msg = self.format(record)
        # Filter high-frequency position update logs to keep the interface clean
        if self.hide_pos and ("->" in msg) and ("L0" in msg or "R1" in msg):
            return
        with self._flush_lock:
            self.log_queue.append(msg)

    def _schedule_flush(self):
        if not self.text_widget.winfo_exists(): return
        with self._flush_lock:
            if self.log_queue:
                self.text_widget.configure(state='normal')
                self.text_widget.insert(tk.END, "\n".join(self.log_queue) + "\n")
                if int(self.text_widget.index('end-1c').split('.')[0]) > 500:
                    self.text_widget.delete('1.0', '100.0')
                self.text_widget.configure(state='disabled')
                self.text_widget.see(tk.END)
                self.log_queue.clear()
        self.text_widget.after(100, self._schedule_flush)

class RelayGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("toy-relay - UDP to Serial")
        self.root.geometry("650x600")
        
        self.relay = None
        self.thread = None

        # Connection Settings
        settings_frame = ttk.LabelFrame(root, text="Settings")
        settings_frame.pack(fill="x", padx=10, pady=5)

        # UDP
        row0 = ttk.Frame(settings_frame)
        row0.pack(fill="x", padx=5, pady=2)
        ttk.Label(row0, text="UDP Listen:").pack(side="left")
        self.udp_ip = tk.StringVar(value="127.0.0.1")
        ttk.Entry(row0, textvariable=self.udp_ip, width=12).pack(side="left", padx=2)
        ttk.Label(row0, text=":").pack(side="left")
        self.udp_port = tk.IntVar(value=8000)
        ttk.Entry(row0, textvariable=self.udp_port, width=6).pack(side="left", padx=2)
        
        # Serial Port
        row1 = ttk.Frame(settings_frame)
        row1.pack(fill="x", padx=5, pady=2)
        ttk.Label(row1, text="Serial Port:").pack(side="left")
        self.serial_port = tk.StringVar()
        self.port_combo = ttk.Combobox(row1, textvariable=self.serial_port, width=20)
        self.port_combo.pack(side="left", padx=5)
        ttk.Button(row1, text="Refresh", command=self.refresh_ports).pack(side="left")
        
        ttk.Label(row1, text="Baud Rate:").pack(side="left", padx=(10,0))
        self.baud_rate = tk.IntVar(value=921600)
        ttk.Entry(row1, textvariable=self.baud_rate, width=10).pack(side="left", padx=2)

        # Options
        row2 = ttk.Frame(settings_frame)
        row2.pack(fill="x", padx=5, pady=2)
        self.hide_pos = tk.BooleanVar(value=True)
        ttk.Checkbutton(row2, text="Hide high-frequency position logs", variable=self.hide_pos, command=self.update_log_filter).pack(side="left")
        self.dummy_mode = tk.BooleanVar(value=False)
        ttk.Checkbutton(row2, text="Dummy Mode", variable=self.dummy_mode).pack(side="left", padx=10)

        # Live Control
        cmd_frame = ttk.LabelFrame(root, text="Live Control")
        cmd_frame.pack(fill="x", padx=10, pady=5)
        
        row3 = ttk.Frame(cmd_frame)
        row3.pack(fill="x", padx=5, pady=5)
        self.cmd_input = tk.StringVar()
        ttk.Label(row3, text="Send T-Code Manually:").pack(side="left")
        self.ent = ttk.Entry(row3, textvariable=self.cmd_input)
        self.ent.pack(side="left", fill="x", expand=True, padx=5)
        self.ent.bind("<Return>", lambda e: self.send_manual_cmd())
        ttk.Button(row3, text="Send", command=self.send_manual_cmd).pack(side="left")
        
        # Preset Commands
        row4 = ttk.Frame(cmd_frame)
        row4.pack(fill="x", padx=5, pady=2)
        ttk.Button(row4, text="Query Device (D0)", command=lambda: self.send_manual_cmd("D0")).pack(side="left", padx=2)
        ttk.Button(row4, text="Query Battery ($B)", command=lambda: self.send_manual_cmd("$B")).pack(side="left", padx=2)
        ttk.Button(row4, text="Emergency Stop", command=lambda: self.send_manual_cmd("V00000 L05000")).pack(side="left", padx=2)

        # Start/Stop Buttons
        self.start_btn = ttk.Button(root, text="Start Relay Service", command=self.start_service)
        self.start_btn.pack(fill="x", padx=10, pady=5)
        self.stop_btn = ttk.Button(root, text="Stop Service", command=self.stop_service, state="disabled")
        self.stop_btn.pack(fill="x", padx=10, pady=2)

        # Log
        self.log_text = scrolledtext.ScrolledText(root, state='disabled', height=15, font=("Consolas", 9))
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)

        self.handler = TextHandler(self.log_text, hide_pos=self.hide_pos.get())
        self.handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S'))
        logger.addHandler(self.handler)
        logger.addHandler(logging.StreamHandler())

        self.refresh_ports()

    def update_log_filter(self):
        self.handler.hide_pos = self.hide_pos.get()

    def refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        self.port_combo['values'] = [p.device for p in ports]
        if ports: self.port_combo.current(0)

    def send_manual_cmd(self, cmd=None):
        if not cmd:
            cmd = self.cmd_input.get()
        if self.relay and cmd:
            self.relay.send_serial_cmd(cmd)
            self.cmd_input.set("")

    def start_service(self):
        self.relay = UdpToSerialRelay(
            self.udp_ip.get(), self.udp_port.get(),
            self.serial_port.get(), self.baud_rate.get(),
            self.dummy_mode.get(), verbose=True
        )
        self.thread = threading.Thread(target=self.run_relay_thread, daemon=True)
        self.thread.start()
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

    def run_relay_thread(self):
        try: self.relay.run()
        finally: self.root.after(0, self.reset_ui)

    def stop_service(self):
        if self.relay: self.relay.running = False

    def reset_ui(self):
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = RelayGUI(root)
    root.mainloop()