import time
import re

TCODE_REGEX_BYTES = re.compile(br'([a-zA-Z][0-9])([0-9]+(?:[ISis][0-9]+)?)')
packets = [b"L0000\n", b"L1500 I100\n", b"L0999\n", b"R1200\n"]

def orig(packets):
    combined_packet = b"".join(packets)
    axis_state = dict(TCODE_REGEX_BYTES.findall(combined_packet.replace(b" ", b"")))
    if not axis_state: return None
    merged = b" ".join([axis + cmd for axis, cmd in axis_state.items()])
    return merged.upper().decode('ascii', errors='replace') + "\n"

def new1(packets):
    combined_packet = b"".join(packets)
    axis_state = dict(TCODE_REGEX_BYTES.findall(combined_packet.replace(b" ", b"")))
    if not axis_state: return None, None
    merged_bytes = b" ".join([axis + cmd for axis, cmd in axis_state.items()]).upper() + b"\n"
    # Wait, we need the string for websocket broadcast and logging.
    # We need the bytes for serial write.
    # returning a tuple (bytes, string)?
    return merged_bytes, merged_bytes.decode('ascii', errors='replace')

start = time.time()
for _ in range(500000):
    merged_cmd = orig(packets)
    if merged_cmd:
        encoded = merged_cmd.encode()
        stripped = merged_cmd.strip()
print("Orig (decode + encode):", time.time() - start)

start = time.time()
for _ in range(500000):
    merged_bytes, merged_cmd = new1(packets)
    if merged_bytes:
        encoded = merged_bytes
        stripped = merged_cmd.strip()
print("New1 (return bytes + str):", time.time() - start)
