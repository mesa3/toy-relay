import time
# Is there another hot spot?
# Look at the list comprehension in `process_tcode_buffer`
# `merged = b" ".join([axis + cmd for axis, cmd in axis_state.items()])`
# `axis_state.items()` creates tuples, unpacks to `axis, cmd`, then `axis + cmd`.
# Since `axis_state` comes from `dict(TCODE_REGEX_BYTES.findall(...))`,
# What if we use a regex that captures `axis + cmd` as the value?
# Oh wait! We tried that. It was faster!

# From test_perf14.py:
"""
TCODE_REGEX_WHOLE = re.compile(br'(([a-zA-Z][0-9])[0-9]+(?:[ISis][0-9]+)?)')

def new1():
    combined_packet = b"".join(packets).replace(b" ", b"")
    matches = TCODE_REGEX_WHOLE.findall(combined_packet)
    if not matches: return None
    axis_state = {k: v for v, k in matches}
    merged = b" ".join(list(axis_state.values()))
    return merged.upper().decode('ascii', errors='replace') + "\n"
"""
# "New1 (whole regex + dict comp): 2.0491626262664795" vs "Orig: 2.2293860912323"
# That's an ~8% improvement in parsing logic!

# Let's verify `TCODE_REGEX_WHOLE` with edge cases.
import re

TCODE_REGEX_BYTES = re.compile(br'([a-zA-Z][0-9])([0-9]+(?:[ISis][0-9]+)?)')
TCODE_REGEX_WHOLE = re.compile(br'(([a-zA-Z][0-9])([0-9]+(?:[ISis][0-9]+)?))')

combined_packet = b"L0000L1500I100L0999R1200"

axis_state_orig = dict(TCODE_REGEX_BYTES.findall(combined_packet))
merged_orig = b" ".join([axis + cmd for axis, cmd in axis_state_orig.items()])
res_orig = merged_orig.upper().decode('ascii', errors='replace') + "\n"

matches = TCODE_REGEX_WHOLE.findall(combined_packet)
axis_state_new = {k: v for v, k, _ in matches}
merged_new = b" ".join(axis_state_new.values())
res_new = merged_new.upper().decode('ascii', errors='replace') + "\n"

print("Orig matches:", axis_state_orig)
print("Orig result:", res_orig)
print("New matches:", matches)
print("New dict:", axis_state_new)
print("New result:", res_new)
assert res_orig == res_new

# Let's bench the exact new approach (using 3 groups: full, key, value) vs (full, key).
