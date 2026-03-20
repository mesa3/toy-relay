import time
import re

TCODE_REGEX_BYTES = re.compile(br'([a-zA-Z][0-9])([0-9]+(?:[ISis][0-9]+)?)')
packets1 = [b"L0000\n"]
packets2 = [b"L0000\n", b"L1500 I100\n", b"L0999\n", b"R1200\n"]

def orig(packets):
    combined_packet = b"".join(packets)
    axis_state = dict(TCODE_REGEX_BYTES.findall(combined_packet.replace(b" ", b"")))
    if not axis_state: return None
    merged = b" ".join([axis + cmd for axis, cmd in axis_state.items()])
    return merged.upper().decode('ascii', errors='replace') + "\n"

def new1(packets):
    combined_packet = packets[0] if len(packets) == 1 else b"".join(packets)
    axis_state = dict(TCODE_REGEX_BYTES.findall(combined_packet.replace(b" ", b"")))
    if not axis_state: return None
    merged = b" ".join([axis + cmd for axis, cmd in axis_state.items()])
    return merged.upper().decode('ascii', errors='replace') + "\n"

start = time.time()
for _ in range(500000): orig(packets1)
print("Orig (len=1):", time.time() - start)

start = time.time()
for _ in range(500000): new1(packets1)
print("New1 (len=1):", time.time() - start)
