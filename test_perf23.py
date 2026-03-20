import time
import re

TCODE_REGEX_BYTES = re.compile(br'([a-zA-Z][0-9])([0-9]+(?:[ISis][0-9]+)?)')
TCODE_REGEX_WHOLE2 = re.compile(br'(([a-zA-Z][0-9])[0-9]+(?:[ISis][0-9]+)?)')

def orig(packets):
    combined_packet = b"".join(packets)
    axis_state = dict(TCODE_REGEX_BYTES.findall(combined_packet.replace(b" ", b"")))
    if not axis_state: return None
    merged = b" ".join([axis + cmd for axis, cmd in axis_state.items()])
    return merged.upper().decode('ascii', errors='replace') + "\n"

def new2(packets):
    combined_packet = b"".join(packets).replace(b" ", b"")
    matches = TCODE_REGEX_WHOLE2.findall(combined_packet)
    if not matches: return None
    # matches is a list of tuples: `[(full, key), ...]`
    # We want `{key: full}`
    axis_state = {k: v for v, k in matches}
    merged = b" ".join(axis_state.values())
    return merged.upper().decode('ascii', errors='replace') + "\n"

packets = [b"L0000\n", b"L1500 I100\n", b"L0999\n", b"R1200\n"]

start = time.time()
for _ in range(500000): orig(packets)
print("Orig:", time.time() - start)

start = time.time()
for _ in range(500000): new2(packets)
print("New2:", time.time() - start)
