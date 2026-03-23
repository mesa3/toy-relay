import time
# Is `select.select([self.sock], [], [], 0.01)` slow?
# Can we do `self.sock.recvfrom` directly and catch `BlockingIOError` without `select`?
# In python, `select` timeout gives us a sleep if there is no data.
# `while self.running:`
#    `readable, _, _ = select.select([self.sock], [], [], 0.01)`
# If there's no data, it sleeps for 0.01s.
# If we do `data = recvfrom()` and it throws `BlockingIOError`, we would have to `time.sleep(0.01)` manually, which is the same or worse.

# Look at `UdpToSerialRelay.send_serial_cmd`:
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
# `hasattr(self, 'ws_server')` is checked every time. `self.ws_server` is always an attribute. It defaults to `None`.
# So `hasattr` is redundant and adds overhead.
# Also, `cmd_str.endswith('\n')` creates a boolean, then `cmd_str += '\n'` adds a newline.

# If this is called frequently, optimizing `send_serial_cmd` would help.
