import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    new_mode_block = '''
            elif self.motion_mode == "glans_torture":
                # Glans Torture (龟头折磨)
                # Devices stay at the far extension limit (top of the stroke) and vibrate/knead intensely.

                # Shift the center L0 to the far end (simulate staying at the tip)
                # We use amp_l0 as the offset to push it out.
                tip_center_l0 = center_l0 + (amp_l0 * 0.8)

                # High frequency, micro amplitude
                micro_amp_l0 = amp_l0 * 0.15
                fast_phase = phase_a * 4.0 # 4x speed vibration

                # Micro vertical vibration
                z_motion = micro_amp_l0 * math.sin(fast_phase)

                pos_l0 = tip_center_l0 + z_motion

                # L2 compensates the new tip center + micro vibration to stay on the parallel track
                base_l2_offset = amp_l0 * 0.8 * l2_mult
                micro_l2_offset = z_motion * l2_mult

                pos_a_l2 = center_l2 - base_l2_offset - micro_l2_offset
                pos_b_l2 = center_l2 + base_l2_offset + micro_l2_offset

                # Intense, fast kneading (R1 Roll + R2 Pitch)
                pos_a_r1 = center_a_r1 + (amp_r1 * 0.5) * math.sin(fast_phase * 1.5)
                pos_b_r1 = center_b_r1 - (amp_r1 * 0.5) * math.sin(fast_phase * 1.5)

                pos_a_r2 = center_r2 + (amp_r2 * 0.5) * math.cos(fast_phase)
                pos_b_r2 = center_r2 - (amp_r2 * 0.5) * math.cos(fast_phase)

                cmd_a_parts.extend([f"L0{clamp(pos_l0):04d}", f"L2{clamp(pos_a_l2):04d}", f"R2{clamp(pos_a_r2):04d}", f"R1{clamp(pos_a_r1):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_l0):04d}", f"L2{clamp(pos_b_l2):04d}", f"R2{clamp(pos_b_r2):04d}", f"R1{clamp(pos_b_r1):04d}"])
'''
    target = '            elif self.motion_mode == "single_foot_tease_left":'
    content = content.replace(target, new_mode_block + target)

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
print("Glans torture added")
