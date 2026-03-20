import time
# Is `[client.send(message) for client in self.clients]` evaluated lazily or does it create a list of coros?
# It creates a list. `gather(*[...])` unpacks it.
# Can it be written as `gather(*(client.send(message) for client in self.clients))`? Yes.
# "In CPython, using a list comprehension inside `str.join()` or `bytes.join()` for small-to-medium collections is measurably faster (~40%) than a generator expression."
# This refers to `join()`. For `gather(*(...))`, unpacking a generator expression allocates a list internally anyway (or tuple), so list comprehension is faster or identical.

# Look at `serial_to_udp_loop`:
"""
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
"""

# Let's check `recvfrom` loop again.
# "recvfrom = self.sock.recvfrom
#  append_packet = packets.append
#  while True:
#      try:
#          data, addr = recvfrom(4096)
#          if data:
#              append_packet(data)
#              self.last_udp_addr = addr
#      except OSError:
#          break"
# The journal says: "recvfrom rarely returns empty data unless explicitly sent 0-byte packets, so `if data:` is often redundant."
# And memory says: "Performance Optimization Pattern: In tight data-ingestion loops (like UDP packet reading), caching the list append method locally (e.g., `append_packet = packets.append`) and removing redundant data checks when exceptions inherently handle empty states can yield measurable throughput gains."
# Wait! I was told by the code reviewer that my optimization was hallucinated and functionally incorrect because it doesn't handle 0-byte packets!
