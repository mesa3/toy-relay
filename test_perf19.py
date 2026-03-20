import time
# Let's check `serial_to_udp_loop`:
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
# `self.dummy and self.ser and self.ser.is_open` is evaluated on every iteration.
# Can we move it out or cache it? No, because `self.ser` could be closed, or `dummy` could be changed (though unlikely).
# But what if we do `ser = self.ser` inside the loop? Wait, `ser.readline` blocks for up to `0.01` seconds (timeout).
# If `ser` is None or dummy, it sleeps for `0.01` seconds.

# Wait, the `serial.readline` timeout is set to `0.01` when opening the connection.
# Every time `readline` is called, if there's no data, it takes `0.01` seconds.
# So if `self.ser` is open, it takes `0.01` seconds anyway unless there's data.

# Look at `time.time()` inside `run()`:
"""
                # Safety watchdog
                if not self.watchdog_triggered and (time.time() - self.last_receive_time > 2.0):
"""
# `time.time()` is called on every loop iteration (~0.01s).
# Memory says: "Always move system calls, object creation, and variable assignment outside the tight loops, or do it once per batch, so it only runs when necessary."
# "self.last_receive_time = time.time()" is done when `packets` is not empty.
# But for the watchdog, `time.time()` is evaluated every loop iteration, even when no packets were received!
# Can we optimize this by caching `time.time()` in `select` timeout, or checking watchdog less frequently?
# Or just accept `time.time()`? `time.time()` is very fast in Python (around 40-50ns).

# What about `select.select([self.sock], [], [], 0.01)`?
# If there are NO packets, the watchdog check evaluates `time.time()`.
# If we do `current_time = time.time()` after `select` returns?
# Is there a better optimization?
