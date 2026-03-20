import time
import re

# original
TCODE_REGEX_BYTES = re.compile(br'([a-zA-Z][0-9])([0-9]+(?:[ISis][0-9]+)?)')

# What if we capture the whole thing and also the key?
TCODE_REGEX_WHOLE = re.compile(br'(([a-zA-Z][0-9])[0-9]+(?:[ISis][0-9]+)?)')
# re.findall returns a list of tuples like (full_match, key)
# dict(reversed_tuples) ?

packets = [b"L0000\n", b"L1500 I100\n", b"L0999\n", b"R1200\n"]

def orig():
    combined_packet = b"".join(packets)
    axis_state = dict(TCODE_REGEX_BYTES.findall(combined_packet.replace(b" ", b"")))
    if not axis_state: return None
    merged = b" ".join([axis + cmd for axis, cmd in axis_state.items()])
    return merged.upper().decode('ascii', errors='replace') + "\n"

def new1():
    combined_packet = b"".join(packets).replace(b" ", b"")

    # We want dict comprehension with `key` as the map key and `full_match` as the value
    # But `findall` gives `[(full_match, key), ...]`
    # wait: `(([a-zA-Z][0-9])[0-9]+(?:[ISis][0-9]+)?)` -> `(full_match, key)`
    # dict() will make `full_match` the key and `key` the value.
    # If we swap the order in regex? Python regex doesn't let us easily return group 2 then group 1.

    matches = TCODE_REGEX_WHOLE.findall(combined_packet)
    if not matches: return None

    # So we use `{k: v for v, k in matches}`
    # Wait, dictionary insertion order matters for the final join order?
    # Python 3.7+ dict preserves insertion order.
    axis_state = {k: v for v, k in matches}

    merged = b" ".join(list(axis_state.values()))
    return merged.upper().decode('ascii', errors='replace') + "\n"


start = time.time()
for _ in range(500000): orig()
print("Orig:", time.time() - start)

start = time.time()
for _ in range(500000): new1()
print("New1 (whole regex + dict comp):", time.time() - start)
