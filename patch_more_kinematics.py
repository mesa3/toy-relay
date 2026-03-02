import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # sole_rub - uses pure R2/R1, L0 is constant. Keep it as is but add L1 constant
    sole_rub_old = '''            elif self.motion_mode == "sole_rub":
                pos_a_r2 = center_r2 + amp_r2 * math.sin(phase_a)
                pos_b_r2 = center_r2 + amp_r2 * math.sin(phase_b)

                pos_a_r1 = center_rx + amp_r1 * math.cos(phase_a)
                pos_b_r1 = center_rx + amp_r1 * math.cos(phase_b)

                cmd_a_parts.extend([f"L0{clamp(center_l0):04d}", f"R2{clamp(pos_a_r2):04d}", f"R1{clamp(pos_a_r1):04d}"])
                cmd_b_parts.extend([f"L0{clamp(center_l0):04d}", f"R2{clamp(pos_b_r2):04d}", f"R1{clamp(pos_b_r1):04d}"])'''

    sole_rub_new = '''            elif self.motion_mode == "sole_rub":
                pos_a_r2 = center_r2 + amp_r2 * math.sin(phase_a)
                pos_b_r2 = center_r2 + amp_r2 * math.sin(phase_b)

                pos_a_r1 = center_rx + amp_r1 * math.cos(phase_a)
                pos_b_r1 = center_rx + amp_r1 * math.cos(phase_b)

                cmd_a_parts.extend([f"L0{clamp(center_l0):04d}", f"L1{clamp(center_l1):04d}", f"R2{clamp(pos_a_r2):04d}", f"R1{clamp(pos_a_r1):04d}"])
                cmd_b_parts.extend([f"L0{clamp(center_l0):04d}", f"L1{clamp(center_l1):04d}", f"R2{clamp(pos_b_r2):04d}", f"R1{clamp(pos_b_r1):04d}"])'''
    content = content.replace(sole_rub_old, sole_rub_new)

    # toe tease - adds L1 constant
    toe_tease_old = '''            elif self.motion_mode == "toe_tease":
                # Quick flickering pitch (R2) to tap the toes.
                # L0 remains relatively steady but close.
                # Use a 2x frequency multiplier for a faster "teasing" feel.
                fast_phase_a = phase_a * 2.0
                fast_phase_b = phase_b * 2.0

                # Toes point "down" to tap towards the center
                # Assuming R2 < 5000 is pointing toes down. We sweep between 5000 and (5000 - amp_r2)
                pos_a_r2 = center_r2 - (amp_r2 / 2.0) - (amp_r2 / 2.0) * math.sin(fast_phase_a)
                pos_b_r2 = center_r2 - (amp_r2 / 2.0) - (amp_r2 / 2.0) * math.sin(fast_phase_b)

                # Small L0 stroke to assist tapping
                pos_a_l0 = center_l0 + (amp_l0 / 4.0) * math.cos(fast_phase_a)
                pos_b_l0 = center_l0 + (amp_l0 / 4.0) * math.cos(fast_phase_b)

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"R2{clamp(pos_b_r2):04d}"])'''
    toe_tease_new = '''            elif self.motion_mode == "toe_tease":
                # Quick flickering pitch (R2) to tap the toes.
                fast_phase_a = phase_a * 2.0
                fast_phase_b = phase_b * 2.0

                pos_a_r2 = center_r2 - (amp_r2 / 2.0) - (amp_r2 / 2.0) * math.sin(fast_phase_a)
                pos_b_r2 = center_r2 - (amp_r2 / 2.0) - (amp_r2 / 2.0) * math.sin(fast_phase_b)

                # Small L0 stroke to assist tapping, with L1 compensation to keep toes aligned to center
                z_motion_a = (amp_l0 / 4.0) * math.cos(fast_phase_a)
                z_motion_b = (amp_l0 / 4.0) * math.cos(fast_phase_b)

                pos_a_l0 = center_l0 + z_motion_a
                pos_b_l0 = center_l0 + z_motion_b

                pos_a_l1 = center_l1 - z_motion_a
                pos_b_l1 = center_l1 + z_motion_b

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"L1{clamp(pos_a_l1):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"L1{clamp(pos_b_l1):04d}", f"R2{clamp(pos_b_r2):04d}"])'''
    content = content.replace(toe_tease_old, toe_tease_new)

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
print("More patched")
