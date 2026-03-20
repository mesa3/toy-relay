import time
import re

TCODE_REGEX_BYTES = re.compile(br'([a-zA-Z][0-9])([0-9]+(?:[ISis][0-9]+)?)')
# We can make a simplified regex if we know it's already uppercase
TCODE_REGEX_BYTES_UPPER = re.compile(br'([A-Z][0-9])([0-9]+(?:[IS][0-9]+)?)')

packets = [b"l0000\n", b"L1500 i100\n", b"l0999\n", b"R1200\n"]

def orig():
    combined_packet = b"".join(packets)
    axis_state = dict(TCODE_REGEX_BYTES.findall(combined_packet.replace(b" ", b"")))
    if not axis_state: return None
    merged = b" ".join([axis + cmd for axis, cmd in axis_state.items()])
    return merged.upper().decode('ascii', errors='replace') + "\n"

def new1():
    combined_packet = b"".join(packets).replace(b" ", b"").upper()
    axis_state = dict(TCODE_REGEX_BYTES_UPPER.findall(combined_packet))
    if not axis_state: return None
    merged = b" ".join([axis + cmd for axis, cmd in axis_state.items()])
    return merged.decode('ascii', errors='replace') + "\n"


def new2():
    # Only upper the resulting dict items instead of the whole string?
    pass

start = time.time()
for _ in range(500000): orig()
print("Orig:", time.time() - start)

start = time.time()
for _ in range(500000): new1()
print("New1 (upper + simple regex):", time.time() - start)
