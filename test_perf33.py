import time
# wait, cmd_str is passed as `str`, it might be empty. `cmd_str[-1]` could raise IndexError.
# `cmd_str.endswith('\n')` is safe.
# Actually, the optimization in `send_serial_cmd` is very minor, but `process_tcode_buffer` is called heavily.
# Wait, look at `serial_to_udp_loop`:
"""
                try:
                    line = self.ser.readline()
                    if line:
                        # ⚡ Optimized: Strip byte line before decoding to prevent creating
                        # string objects and overhead when dealing with empty/whitespace feedback lines.
                        stripped = line.strip()
                        if stripped:
                            decoded = stripped.decode(errors='replace')
                            logger.info(f"<- [Device Feedback] {decoded}")
                            if self.last_udp_addr:
                                self.sock.sendto(line, self.last_udp_addr)
                            # ⚡ Optimized: If a line was read, immediately continue to drain the buffer
                            # without artificial delay, maximizing feedback throughput.
                            continue
                except Exception:
                    pass
            time.sleep(0.01)
"""
# If `self.ser.readline()` returns `b''` due to timeout, `if line:` is False.
# Then it goes to `time.sleep(0.01)`.
# But `readline` ALREADY blocks for `self.ser.timeout` which is `0.01`.
# So it sleeps twice!
# Timeout in `serial.Serial` is `0.01`. If it reads nothing, it takes `0.01s` and then returns empty bytes.
# Then `time.sleep(0.01)` adds another `0.01s`.
# By removing `time.sleep(0.01)` when `self.ser.is_open` is true, we can double the feedback polling rate!
