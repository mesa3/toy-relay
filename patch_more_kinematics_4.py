import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # single_foot_stroke_left
    sfl_old = '''            elif self.motion_mode == "single_foot_stroke_left":
                # Left foot strokes with pitch compensation, Right foot holds still
                pos_a_l0 = center_l0 + amp_l0 * math.sin(phase_a)
                pos_a_r2 = center_r2 + amp_r2 * math.sin(phase_a)

                pos_b_l0 = center_l0
                pos_b_r2 = center_r2

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"R2{clamp(pos_b_r2):04d}"])'''

    sfl_new = '''            elif self.motion_mode == "single_foot_stroke_left":
                z_motion_a = amp_l0 * math.sin(phase_a)
                pos_a_l0 = center_l0 + z_motion_a
                pos_a_l1 = center_l1 - z_motion_a

                pos_b_l0 = center_l0
                pos_b_l1 = center_l1

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"L1{clamp(pos_a_l1):04d}", f"R2{clamp(center_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"L1{clamp(pos_b_l1):04d}", f"R2{clamp(center_r2):04d}"])'''
    content = content.replace(sfl_old, sfl_new)

    # single_foot_stroke_right
    sfr_old = '''            elif self.motion_mode == "single_foot_stroke_right":
                # Right foot strokes with pitch compensation, Left foot holds still
                pos_a_l0 = center_l0
                pos_a_r2 = center_r2

                pos_b_l0 = center_l0 + amp_l0 * math.sin(phase_a) # Use phase_a for the active foot
                pos_b_r2 = center_r2 + amp_r2 * math.sin(phase_a)

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"R2{clamp(pos_b_r2):04d}"])'''

    sfr_new = '''            elif self.motion_mode == "single_foot_stroke_right":
                pos_a_l0 = center_l0
                pos_a_l1 = center_l1

                z_motion_b = amp_l0 * math.sin(phase_a) # Use phase_a for the active foot
                pos_b_l0 = center_l0 + z_motion_b
                pos_b_l1 = center_l1 + z_motion_b

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"L1{clamp(pos_a_l1):04d}", f"R2{clamp(center_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"L1{clamp(pos_b_l1):04d}", f"R2{clamp(center_r2):04d}"])'''
    content = content.replace(sfr_old, sfr_new)

    # wrapping_twist
    wt_old = '''            elif self.motion_mode == "wrapping_twist":
                # Hold a constant close squeeze (L0).
                # Roll soles inwards (R1). Assuming +R1 is roll inwards for left foot, then -R1 is inwards for right foot.
                # (Or vice versa, they should be out of phase to roll symmetrically relative to the center).
                pos_a_r1 = center_rx + amp_r1 * math.sin(phase_a)
                pos_b_r1 = center_rx - amp_r1 * math.sin(phase_a) # Mirror roll inwards

                # Twist soles (R0) around the center axis
                pos_a_r0 = center_rx + amp_r0 * math.cos(phase_a)
                pos_b_r0 = center_rx - amp_r0 * math.cos(phase_a) # Mirror twist

                cmd_a_parts.extend([f"L0{clamp(center_l0):04d}", f"R1{clamp(pos_a_r1):04d}", f"R0{clamp(pos_a_r0):04d}"])
                cmd_b_parts.extend([f"L0{clamp(center_l0):04d}", f"R1{clamp(pos_b_r1):04d}", f"R0{clamp(pos_b_r0):04d}"])'''

    wt_new = '''            elif self.motion_mode == "wrapping_twist":
                # Hold a constant close squeeze (L0) and center (L1)
                pos_a_r1 = center_rx + amp_r1 * math.sin(phase_a)
                pos_b_r1 = center_rx - amp_r1 * math.sin(phase_a) # Mirror roll inwards

                pos_a_r0 = center_rx + amp_r0 * math.cos(phase_a)
                pos_b_r0 = center_rx - amp_r0 * math.cos(phase_a) # Mirror twist

                cmd_a_parts.extend([f"L0{clamp(center_l0):04d}", f"L1{clamp(center_l1):04d}", f"R1{clamp(pos_a_r1):04d}", f"R0{clamp(pos_a_r0):04d}"])
                cmd_b_parts.extend([f"L0{clamp(center_l0):04d}", f"L1{clamp(center_l1):04d}", f"R1{clamp(pos_b_r1):04d}", f"R0{clamp(pos_b_r0):04d}"])'''
    content = content.replace(wt_old, wt_new)


    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
print("More patched 4")
