import time
import re

TCODE_REGEX_BYTES = re.compile(br'([a-zA-Z][0-9])([0-9]+(?:[ISis][0-9]+)?)')

def orig(packets):
    combined_packet = b"".join(packets)
    axis_state = dict(TCODE_REGEX_BYTES.findall(combined_packet.replace(b" ", b"")))
    if not axis_state: return None
    merged = b" ".join([axis + cmd for axis, cmd in axis_state.items()])
    return merged.upper().decode('ascii', errors='replace') + "\n"

# Can we do `re.finditer`?
def new1(packets):
    combined_packet = b"".join(packets).replace(b" ", b"")
    axis_state = {m.group(1): m.group(0) for m in re.finditer(br'([a-zA-Z][0-9])[0-9]+(?:[ISis][0-9]+)?', combined_packet)}
    if not axis_state: return None
    merged = b" ".join(axis_state.values())
    return merged.upper().decode('ascii', errors='replace') + "\n"

packets = [b"L0000\n", b"L1500 I100\n", b"L0999\n", b"R1200\n"]

start = time.time()
for _ in range(500000): orig(packets)
print("Orig:", time.time() - start)

start = time.time()
for _ in range(500000): new1(packets)
print("New1 (finditer):", time.time() - start)
