import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    new_mode_block = '''
            elif self.motion_mode == "foot_slap":
                # Foot Slap (脚耳光)
                # One foot holds back, suddenly strikes (sharp peak), and immediately retreats. Alternating.

                # Slow phase controls the rhythm of the slaps (e.g., 1 slap every full cycle)
                turn_phase = phase_a * 0.5

                # We use a mathematical trick to create a sharp "slap" profile instead of a smooth sine wave.
                # max(0, sin(x))^8 creates a flat zero baseline with sudden, sharp peaks.
                raw_slap_a = max(0, math.sin(phase_a * 2.0)) ** 8
                raw_slap_b = max(0, math.sin(phase_a * 2.0 + math.pi)) ** 8

                # Only let A slap if turn_phase is positive, B if negative (interleaving them with pauses)
                # Actually, let's just make them alternate rhythmically without long pauses, like being slapped left and right.
                z_motion_a = amp_l0 * raw_slap_a
                z_motion_b = amp_l0 * raw_slap_b

                # Slap is just a fast L0 push, but we want it to be parallel too
                pos_a_l0 = center_l0 + z_motion_a
                pos_a_l2 = center_l2 - (z_motion_a * l2_mult)

                pos_b_l0 = center_l0 + z_motion_b
                pos_b_l2 = center_l2 + (z_motion_b * l2_mult)

                # Accompanied by a sharp pitch to mimic the "snap" of an ankle during a slap
                pos_a_r2 = center_r2 + (amp_r2 * raw_slap_a)
                pos_b_r2 = center_r2 - (amp_r2 * raw_slap_b)

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"L2{clamp(pos_a_l2):04d}", f"R2{clamp(pos_a_r2):04d}", f"R1{clamp(center_a_r1):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"L2{clamp(pos_b_l2):04d}", f"R2{clamp(pos_b_r2):04d}", f"R1{clamp(center_b_r1):04d}"])
'''
    target = '            elif self.motion_mode == "single_foot_tease_left":'
    content = content.replace(target, new_mode_block + target)

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
print("Foot slap added")
