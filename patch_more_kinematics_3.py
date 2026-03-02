import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # circling_tease
    circ_old = '''            elif self.motion_mode == "circling_tease":
                # Feet held gently on the target.
                # Roll (R1) and Pitch (R2) move in a circular sine/cosine pattern to create a grinding orbital motion.
                pos_a_r1 = center_rx + amp_r1 * math.sin(phase_a)
                pos_b_r1 = center_rx - amp_r1 * math.sin(phase_a) # mirror roll

                pos_a_r2 = center_r2 + amp_r2 * math.cos(phase_a)
                pos_b_r2 = center_r2 + amp_r2 * math.cos(phase_a) # sync pitch

                cmd_a_parts.extend([f"L0{clamp(center_l0):04d}", f"R1{clamp(pos_a_r1):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(center_l0):04d}", f"R1{clamp(pos_b_r1):04d}", f"R2{clamp(pos_b_r2):04d}"])'''

    circ_new = '''            elif self.motion_mode == "circling_tease":
                pos_a_r1 = center_rx + amp_r1 * math.sin(phase_a)
                pos_b_r1 = center_rx - amp_r1 * math.sin(phase_a)

                pos_a_r2 = center_r2 + amp_r2 * math.cos(phase_a)
                pos_b_r2 = center_r2 + amp_r2 * math.cos(phase_a)

                cmd_a_parts.extend([f"L0{clamp(center_l0):04d}", f"L1{clamp(center_l1):04d}", f"R1{clamp(pos_a_r1):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(center_l0):04d}", f"L1{clamp(center_l1):04d}", f"R1{clamp(pos_b_r1):04d}", f"R2{clamp(pos_b_r2):04d}"])'''
    content = content.replace(circ_old, circ_new)

    # single_foot_tease_left
    sfl_old = '''            elif self.motion_mode == "single_foot_tease_left":
                # Left foot teases with rapid flickering pitch, Right foot stays still at base squeeze
                fast_phase_a = phase_a * 2.0

                # Active Left (Device A)
                pos_a_r2 = center_r2 - (amp_r2 / 2.0) - (amp_r2 / 2.0) * math.sin(fast_phase_a)
                pos_a_l0 = center_l0 + (amp_l0 * 0.1) * math.sin(phase_a)

                # Static Right (Device B)
                pos_b_r2 = center_r2
                pos_b_l0 = center_l0

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"R2{clamp(pos_b_r2):04d}"])'''

    sfl_new = '''            elif self.motion_mode == "single_foot_tease_left":
                # Left foot teases with rapid flickering pitch, Right foot stays still at base squeeze
                fast_phase_a = phase_a * 2.0

                # Active Left (Device A)
                pos_a_r2 = center_r2 - (amp_r2 / 2.0) - (amp_r2 / 2.0) * math.sin(fast_phase_a)

                z_motion_a = (amp_l0 * 0.1) * math.sin(phase_a)
                pos_a_l0 = center_l0 + z_motion_a
                pos_a_l1 = center_l1 - z_motion_a

                # Static Right (Device B)
                pos_b_r2 = center_r2
                pos_b_l0 = center_l0
                pos_b_l1 = center_l1

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"L1{clamp(pos_a_l1):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"L1{clamp(pos_b_l1):04d}", f"R2{clamp(pos_b_r2):04d}"])'''
    content = content.replace(sfl_old, sfl_new)

    # single_foot_tease_right
    sfr_old = '''            elif self.motion_mode == "single_foot_tease_right":
                fast_phase_a = phase_a * 2.0

                # Static Left (Device A)
                pos_a_r2 = center_r2
                pos_a_l0 = center_l0

                # Active Right (Device B)
                pos_b_r2 = center_r2 - (amp_r2 / 2.0) - (amp_r2 / 2.0) * math.sin(fast_phase_a)
                pos_b_l0 = center_l0 + (amp_l0 * 0.1) * math.sin(phase_a)

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"R2{clamp(pos_b_r2):04d}"])'''

    sfr_new = '''            elif self.motion_mode == "single_foot_tease_right":
                fast_phase_a = phase_a * 2.0

                # Static Left (Device A)
                pos_a_r2 = center_r2
                pos_a_l0 = center_l0
                pos_a_l1 = center_l1

                # Active Right (Device B)
                pos_b_r2 = center_r2 - (amp_r2 / 2.0) - (amp_r2 / 2.0) * math.sin(fast_phase_a)

                z_motion_b = (amp_l0 * 0.1) * math.sin(phase_a)
                pos_b_l0 = center_l0 + z_motion_b
                pos_b_l1 = center_l1 + z_motion_b

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"L1{clamp(pos_a_l1):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"L1{clamp(pos_b_l1):04d}", f"R2{clamp(pos_b_r2):04d}"])'''
    content = content.replace(sfr_old, sfr_new)

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
print("More patched 3")
