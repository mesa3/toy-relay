import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # In wave_rub_up_down, R1 rolls.
    # Currently:
    # pos_a_r1 = center_a_r1 + amp_r1 * math.cos(phase_a)
    # pos_b_r1 = center_b_r1 - amp_r1 * math.cos(phase_a) # Mirror roll
    # "Mirror roll" with minus sign means they tilt the same physical direction.
    # To make them alternate (one goes up while the other goes down), we just make them both + amp_r1 * math.cos

    # Wait, if `center_a_r1` and `center_b_r1` are mirrored (one is 9999-x),
    # to move in the same absolute direction, you subtract.
    # Example: A center=1000, B center=8999.
    # A moves to 2000 (up). B needs to move to 7999 (down relative to device, but same physical direction).
    # So pos_b_r1 = center_b_r1 - amp.
    # To make them alternate (A goes up, B goes up relative to device = opposite physical direction):
    # pos_b_r1 = center_b_r1 + amp.

    content = content.replace(
        "pos_b_r1 = center_b_r1 - amp_r1 * math.cos(phase_a) # Mirror roll",
        "pos_b_r1 = center_b_r1 + amp_r1 * math.cos(phase_a) # Alternating phase (+ instead of -)"
    )

    # Now for wave_rub_front_back, we need fast frequency AND alternating phase
    # R2 is pitch. There is no mirrored center for R2, they both use center_r2.
    # Currently:
    # pos_a_r2 = center_r2 + amp_r2 * math.cos(phase_a)
    # pos_b_r2 = center_r2 - amp_r2 * math.cos(phase_a) # Mirror pitch
    # To make it alternate AND fast:

    fast_r2_old = '''                # R2 pitches dynamically to wipe front/back
                pos_a_r2 = center_r2 + amp_r2 * math.cos(phase_a)
                pos_b_r2 = center_r2 - amp_r2 * math.cos(phase_a) # Mirror pitch'''

    fast_r2_new = '''                # R2 pitches dynamically to wipe front/back at a higher frequency (2x)
                fast_phase = phase_a * 2.0
                pos_a_r2 = center_r2 + amp_r2 * math.cos(fast_phase)
                pos_b_r2 = center_r2 - amp_r2 * math.cos(fast_phase) # Alternating rapid pitch'''

    content = content.replace(fast_r2_old, fast_r2_new)

    # Let's do the same for static_rub_front_back
    static_r2_old = '''                # R2 pitches dynamically to wipe front/back
                pos_a_r2 = center_r2 + amp_r2 * math.cos(phase_a)
                pos_b_r2 = center_r2 - amp_r2 * math.cos(phase_a) # Mirror pitch'''

    static_r2_new = '''                # R2 pitches dynamically to wipe front/back at a higher frequency (2x)
                fast_phase = phase_a * 2.0
                pos_a_r2 = center_r2 + amp_r2 * math.cos(fast_phase)
                pos_b_r2 = center_r2 - amp_r2 * math.cos(fast_phase) # Alternating rapid pitch'''

    content = content.replace(static_r2_old, static_r2_new)

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
