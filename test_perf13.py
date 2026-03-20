import time
import re

TCODE_REGEX_BYTES = re.compile(br'([a-zA-Z][0-9])([0-9]+(?:[ISis][0-9]+)?)')
packets = [b"L0000\n", b"L1500 I100\n", b"L0999\n", b"R1200\n"]

def orig():
    combined_packet = b"".join(packets)
    axis_state = dict(TCODE_REGEX_BYTES.findall(combined_packet.replace(b" ", b"")))
    if not axis_state: return None
    merged = b" ".join([axis + cmd for axis, cmd in axis_state.items()])
    return merged.upper().decode('ascii', errors='replace') + "\n"

def new1():
    combined_packet = b"".join(packets).replace(b" ", b"")
    axis_state = dict(TCODE_REGEX_BYTES.findall(combined_packet))
    if not axis_state: return None
    # Use direct byte concatenation without loop if possible? No.
    # What if we just use dict.values()? We need `axis + cmd`... wait!
    # TCODE_REGEX_BYTES has TWO groups: ([a-zA-Z][0-9]) and ([0-9]+(?:[ISis][0-9]+)?)
    # What if we change the regex to capture the FULL command as one group?
    pass
