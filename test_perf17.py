import time
import re

# `process_tcode_buffer` is in a hot loop (once every 10ms at most).
# We saw earlier that simplifying the `recvfrom` loop by consolidating the list appending loop into the `select` is an option, but the current loop is already very optimized.

# Wait, `TCODE_REGEX_BYTES = re.compile(br'([a-zA-Z][0-9])([0-9]+(?:[ISis][0-9]+)?)')`
# Memory says: "In CPython (observed in 3.12), using a list comprehension inside `str.join()` or `bytes.join()` for small-to-medium collections is measurably faster (~40%) than a generator expression."

# Memory says: "Performance Optimization Pattern: For ASCII-only protocols (like T-Code), performing byte-level operations (e.g., `b_string.upper()`) and then decoding strictly as ASCII (`.decode('ascii')`) is measurably faster than decoding to UTF-8 first and applying string operations."

# The codebase already has these applied. Let's look at `TCodeWSServer.broadcast`.
# `asyncio.run_coroutine_threadsafe(self._broadcast_coro(message), self.loop)` is called for every broadcast.

# "If a line was read, immediately continue to drain the buffer without artificial delay, maximizing feedback throughput."
# This is also applied.

# Let's read `serial_to_udp_loop` again.
# "line = self.ser.readline()"
# In dummy mode:
# "if not self.dummy and self.ser and self.ser.is_open:"
# Then it does `time.sleep(0.01)` inside `while self.running:`.
# When the serial is open, it reads a line. If the line is empty (due to timeout), it sleeps `time.sleep(0.01)`.
# If the line is NOT empty, it continues without sleep. This is optimal.

# What about GUI logging?
# `msg = self.format(record)`
# `if self.hide_pos and ("->" in msg) and ("L0" in msg or "R1" in msg): return`
# This happens in the logger thread.
