import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # Inject kinematics block
    new_mode_block = '''
            elif self.motion_mode == "asymmetric_sprint":
                # Asymmetric Sprint (双机非对称冲刺)
                # One foot strokes rapidly while the other holds still, then they switch.

                # Slow phase controls the turn (e.g., switch every 2.5 full cycles)
                turn_phase = phase_a * 0.2
                # Fast phase for the sprint
                sprint_phase = phase_a * 2.5

                if math.sin(turn_phase) > 0:
                    # Device A's turn to sprint
                    z_motion_a = amp_l0 * math.sin(sprint_phase)
                    z_motion_b = 0 # B holds still
                else:
                    # Device B's turn to sprint
                    z_motion_a = 0 # A holds still
                    z_motion_b = amp_l0 * math.sin(sprint_phase)

                pos_a_l0 = center_l0 + z_motion_a
                pos_a_l2 = center_l2 - (z_motion_a * l2_mult)

                pos_b_l0 = center_l0 + z_motion_b
                pos_b_l2 = center_l2 + (z_motion_b * l2_mult)

                # Add a little teasing pitch wag to the active foot
                pos_a_r2 = center_r2 + (amp_r2 * 0.5 * math.cos(sprint_phase) if z_motion_a != 0 else 0)
                pos_b_r2 = center_r2 - (amp_r2 * 0.5 * math.cos(sprint_phase) if z_motion_b != 0 else 0)

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"L2{clamp(pos_a_l2):04d}", f"R2{clamp(pos_a_r2):04d}", f"R1{clamp(center_a_r1):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"L2{clamp(pos_b_l2):04d}", f"R2{clamp(pos_b_r2):04d}", f"R1{clamp(center_b_r1):04d}"])
'''
    target = '            elif self.motion_mode == "single_foot_tease_left":'
    content = content.replace(target, new_mode_block + target)

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
print("Logic added")
