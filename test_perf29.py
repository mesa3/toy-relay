import time
# Is there a performance optimization that *doesn't* change the functionality?
# Let's consider `process_tcode_buffer` again.
import re

TCODE_REGEX_BYTES = re.compile(br'([a-zA-Z][0-9])([0-9]+(?:[ISis][0-9]+)?)')

def orig(packets):
    combined_packet = b"".join(packets)
    axis_state = dict(TCODE_REGEX_BYTES.findall(combined_packet.replace(b" ", b"")))
    if not axis_state: return None
    merged = b" ".join([axis + cmd for axis, cmd in axis_state.items()])
    return merged.upper().decode('ascii', errors='replace') + "\n"

def opt(packets):
    # Instead of dict comprehension or anything, we can replace `.replace` with a pre-compiled regex for space removal? No, replace is faster.
    # What if we just do: `b"".join(packets).replace(b" ", b"").upper()` BEFORE regex?
    combined_packet = b"".join(packets).replace(b" ", b"").upper()
    axis_state = dict(TCODE_REGEX_BYTES.findall(combined_packet))
    if not axis_state: return None
    merged = b" ".join([axis + cmd for axis, cmd in axis_state.items()])
    return merged.decode('ascii', errors='replace') + "\n"

# But what if `TCODE_REGEX_BYTES` is run on uppercase?
# `br'([A-Z][0-9])([0-9]+(?:[IS][0-9]+)?)'`

TCODE_REGEX_BYTES_UPPER = re.compile(br'([A-Z][0-9])([0-9]+(?:[IS][0-9]+)?)')

def opt2(packets):
    combined_packet = b"".join(packets).replace(b" ", b"").upper()
    axis_state = dict(TCODE_REGEX_BYTES_UPPER.findall(combined_packet))
    if not axis_state: return None
    merged = b" ".join([axis + cmd for axis, cmd in axis_state.items()])
    return merged.decode('ascii', errors='replace') + "\n"

packets = [b"l0000\n", b"L1500 i100\n", b"l0999\n", b"R1200\n"]

start = time.time()
for _ in range(500000): orig(packets)
print("Orig:", time.time() - start)

start = time.time()
for _ in range(500000): opt(packets)
print("Opt1 (upper on bytes):", time.time() - start)

start = time.time()
for _ in range(500000): opt2(packets)
print("Opt2 (simplified regex):", time.time() - start)
