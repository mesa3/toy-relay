import time
# Is there a way to optimize `select.select([self.sock], [], [], 0.01)`?
# This is blocked by python's `select`.

# Let's consider `process_tcode_buffer` again.
# `axis_state = dict(TCODE_REGEX_BYTES.findall(combined_packet.replace(b" ", b"")))`
# `merged = b" ".join([axis + cmd for axis, cmd in axis_state.items()])`
# `return merged.upper().decode('ascii', errors='replace') + "\n"`
# We already tried this and couldn't get more than 2% improvement.

# What about: "pre-process the bulk string (e.g., `string.replace(' ', '')`) before applying the regex."
# This is already done: `combined_packet.replace(b" ", b"")`.

# What about: "using a list comprehension inside `str.join()` or `bytes.join()` for small-to-medium collections is measurably faster (~40%) than a generator expression."
# This is already done: `b" ".join([axis + cmd for axis, cmd in axis_state.items()])`.

# What about: "using direct string concatenation (`var1 + var2`) inside list comprehensions is measurably faster than using f-strings"
# This is already done: `axis + cmd`.

# What about: "caching object method lookups into local variables (like `recvfrom = self.sock.recvfrom`) before the loop reduces attribute resolution overhead."
# This is already done: `recvfrom = self.sock.recvfrom`, `append_packet = packets.append`.

# Look closely at `recvfrom` loop:
"""
                    packets = []
                    recvfrom = self.sock.recvfrom
                    append_packet = packets.append
                    while True:
                        try:
                            data, addr = recvfrom(4096)
                            if data:
                                append_packet(data)
                                self.last_udp_addr = addr
                        except OSError:
                            break
"""
# The code review said:
# "When a non-blocking socket has no packets available to read, it raises a BlockingIOError (a subclass of OSError).
# When a non-blocking socket receives a valid 0-byte UDP datagram (often used for keep-alives or NAT hole punching), recvfrom successfully returns b'' alongside the address.
# By removing the `if data:` check, the agent has introduced a functional change. The application will now attempt to process and append 0-byte payloads to the serial queue and update the last address, which the original author explicitly intended to ignore."

# So I should optimize `if data:` differently, or optimize `append_packet`?
# What if we only update `self.last_udp_addr = addr` and append if `data` is truthy, but do it without the `if data:` using short-circuiting or just doing the if check?
# Wait, I am Bolt! There's something else we can optimize.
