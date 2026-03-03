import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # 1. Update center_r1 definition
    center_old = '''            center_l2 = 5000
            center_r1 = (self.roll_angle_offset / 100.0) * 9999
            center_r0 = 5000 # Neutral twist
            center_rx = center_r1 # Backwards compatibility for unmodified modes'''

    center_new = '''            center_l2 = 5000
            center_a_r1 = (self.roll_angle_offset / 100.0) * 9999
            center_b_r1 = 9999 - center_a_r1 # Mirror R1 for Device B so they tilt in the same physical direction
            center_r0 = 5000 # Neutral twist
            center_rx = center_a_r1 # Backwards compatibility for unmodified modes'''
    content = content.replace(center_old, center_new)

    # 2. Update pos_a_r1 and pos_b_r1 formulas

    # In v_stroke, alternating_step, wave_rub_up_down, wave_rub_front_back, static_rub_front_back

    # v_stroke:
    content = content.replace(
        "pos_a_r1 = center_r1 + amp_r1 * math.sin(phase_a)",
        "pos_a_r1 = center_a_r1 + amp_r1 * math.sin(phase_a)"
    )
    content = content.replace(
        "pos_b_r1 = center_r1 - amp_r1 * math.sin(phase_a)",
        "pos_b_r1 = center_b_r1 - amp_r1 * math.sin(phase_a)"
    )

    # wave_rub_up_down:
    content = content.replace(
        "pos_a_r1 = center_r1 + amp_r1 * math.cos(phase_a)",
        "pos_a_r1 = center_a_r1 + amp_r1 * math.cos(phase_a)"
    )
    content = content.replace(
        "pos_b_r1 = center_r1 - amp_r1 * math.cos(phase_a)",
        "pos_b_r1 = center_b_r1 - amp_r1 * math.cos(phase_a)"
    )

    # In other places, R1 is just clamped to center_r1. Let's fix those directly.
    content = content.replace("f\"R1{clamp(center_r1):04d}\"", "f\"R1{clamp(center_a_r1):04d}\"")
    # But wait, both A and B arrays extend using `center_r1`.
    # Let's use regex for `cmd_b_parts.extend` that contain `center_a_r1` and fix them to `center_b_r1`.
    # First, globally replace center_r1 with center_a_r1 in the clamp functions.
    content = content.replace("clamp(center_r1)", "clamp(center_a_r1)")

    # Now fix B's extend lines specifically
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'cmd_b_parts.extend' in line and 'center_a_r1' in line:
            lines[i] = line.replace('center_a_r1', 'center_b_r1')
        elif 'pos_b_r1 = center_a_r1' in line:
            lines[i] = line.replace('center_a_r1', 'center_b_r1')

    with open('dual_osr_control.py', 'w') as f:
        f.write('\n'.join(lines))

patch()
print("R1 Mirror patched")
