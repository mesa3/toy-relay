import time
# Is `[client.send(message) for client in self.clients]` evaluated lazily or does it create a list of coros?
# It creates a list. `gather(*[...])` unpacks it.
# Can it be written as `gather(*(client.send(message) for client in self.clients))`? Yes.
# "In CPython, using a list comprehension inside `str.join()` or `bytes.join()` for small-to-medium collections is measurably faster (~40%) than a generator expression."
# This refers to `join()`. For `gather(*(...))`, unpacking a generator expression allocates a list internally anyway (or tuple), so list comprehension is faster or identical.

# What about GUI logging?
# `self.text_widget.insert(tk.END, "\n".join(self.log_queue) + "\n")`
# This is scheduled every 100ms.

# What about the way `merged` is upper-cased?
"""
merged = b" ".join([axis + cmd for axis, cmd in axis_state.items()])
return merged.upper().decode('ascii', errors='replace') + "\n"
"""
# Could we map `str.upper`? No, bytes.upper.
# We tried it and it's basically the same.

# What about caching `.encode()`?
# `self.ser.write(merged_cmd.encode())`
# Wait. `process_tcode_buffer` returns a string: `merged.upper().decode('ascii', errors='replace') + "\n"`
# Then in the loop:
# `merged_cmd = self.process_tcode_buffer(packets)`
# `if not self.dummy and self.ser: self.ser.write(merged_cmd.encode())`

# WHY ARE WE DECODING TO STRING JUST TO ENCODE BACK TO BYTES?!
