import time
# Let's check `send_serial_cmd`:
"""
    def send_serial_cmd(self, cmd_str: str):
        if self.dummy or not self.ser or not self.ser.is_open:
            return
        if not cmd_str.endswith('\n'):
            cmd_str += '\n'
        try:
            if hasattr(self, 'ws_server') and self.ws_server:
                self.ws_server.broadcast(cmd_str.strip())
            self.ser.write(cmd_str.encode())
        except Exception as e:
            logger.error(f"Serial send failed: {e}")
"""

# Let's check `process_tcode_buffer`:
"""
    def process_tcode_buffer(self, packets):
        if not packets:
            return None
        combined_packet = b"".join(packets)
        axis_state = dict(TCODE_REGEX_BYTES.findall(combined_packet.replace(b" ", b"")))

        if not axis_state:
            return None

        merged = b" ".join([axis + cmd for axis, cmd in axis_state.items()])
        return merged.upper().decode('ascii', errors='replace') + "\n"
"""
# If `packets` has length 1?
# In many cases (e.g. 50Hz, local network), `recvfrom` might just return 1 packet per `select.select`.
# `b"".join([packet])` is fast, but `packets[0]` is faster if `len(packets) == 1`.
# Let's bench this.
