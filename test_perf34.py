# Let's verify `serial_to_udp_loop`:
"""
    def serial_to_udp_loop(self):
        while self.running:
            if not self.dummy and self.ser and self.ser.is_open:
                try:
                    line = self.ser.readline()
                    if line:
                        stripped = line.strip()
                        if stripped:
                            decoded = stripped.decode(errors='replace')
                            logger.info(f"<- [Device Feedback] {decoded}")
                            if self.last_udp_addr:
                                self.sock.sendto(line, self.last_udp_addr)
                            continue
                except Exception:
                    pass
            else:
                time.sleep(0.01)
                continue
            # If we are here, we are NOT dummy, ser is open, and line was empty.
            # But ser.readline() already waited for 0.01 timeout.
            # Do we need time.sleep(0.01) again? No.
"""
# The original code:
"""
    def serial_to_udp_loop(self):
        while self.running:
            if not self.dummy and self.ser and self.ser.is_open:
                try:
                    line = self.ser.readline()
                    if line:
                        stripped = line.strip()
                        if stripped:
                            decoded = stripped.decode(errors='replace')
                            logger.info(f"<- [Device Feedback] {decoded}")
                            if self.last_udp_addr:
                                self.sock.sendto(line, self.last_udp_addr)
                            continue
                except Exception:
                    pass
            time.sleep(0.01)
"""
# Wait, if `continue` is reached, it skips `time.sleep(0.01)`.
# If `line` is empty, it does NOT reach `continue`. So it executes `time.sleep(0.01)`.
# Since `self.ser.readline()` blocks for `self.baud_rate` timeout (0.01s in `setup_connections`),
# sleeping again for `0.01s` means we poll at most 50Hz instead of 100Hz when idle.
# That is an artificial delay that halves the polling rate when the line is quiet, making the reaction to the first message slower by up to 0.01s!
# A 0.01s additional delay is a 10ms jitter in feedback.

# Is there any issue if we remove `time.sleep(0.01)` inside the block when `self.ser.is_open` is true?
# If `self.ser.is_open` is true, `readline()` will block and yield CPU during its timeout.
# So `time.sleep` is totally redundant and harmful for reaction time.
# If `not self.dummy and self.ser and self.ser.is_open` is FALSE (e.g. dummy mode or disconnected),
# `time.sleep(0.01)` IS REQUIRED to avoid a tight busy loop.
