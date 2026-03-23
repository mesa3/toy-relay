import time
# Is there any other place?
# How about `TCodeWSServer._broadcast_coro`
# `await asyncio.gather(*[client.send(message) for client in self.clients], return_exceptions=True)`
# It uses list comprehension, which creates a list. `gather` takes positional args.
# It's an async function. Can it be faster? No, this is standard.

# Look at `serial_to_udp_loop`:
"""
                            if self.last_udp_addr:
                                self.sock.sendto(line, self.last_udp_addr)
"""
# `line` is the raw bytes from `readline`. This is very efficient.

# Look at the memory again:
# "Performance Optimization Pattern: If an input string undergoes global whitespace removal (e.g., replace(b' ', b'')) before regex matching, ensure the regular expression is updated to exclude optional whitespace checks (like \s*)."
# This was already checked. The regex doesn't have `\s*`.

# "Performance Optimization Pattern: When parsing batched text-based network commands (like T-Code) from UDP streams, concatenate incoming packets using b''.join(packets) to avoid adding unnecessary delimiters, and perform cleanup (like space removal via .replace(b' ', b'')) in the bytes domain *before* decoding."
# This is already done.

# "Performance Optimization Pattern: In Python high-frequency hot loops, using direct string concatenation (var1 + var2) inside list comprehensions is measurably faster than using f-strings (f'{var1}{var2}') when the operands are already known to be strings."
# This is already done.

# Is there anything else in `process_tcode_buffer`?
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
# If `packets` is a list of byte arrays, `b"".join(packets)` and `combined_packet.replace(b" ", b"")` allocates a new byte array.
# What if we `replace(b" ", b"")` on individual packets BEFORE joining?
