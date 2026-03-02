import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # Add to UI
    ui_old = '''            "wave_rub_up_down", "wave_rub_front_back",'''
    ui_new = '''            "wave_rub_up_down", "wave_rub_front_back", "static_rub_front_back",'''
    content = content.replace(ui_old, ui_new)

    # Add to sync mode list
    sync_old = '''                    "wave_rub_up_down", "wave_rub_front_back",'''
    sync_new = '''                    "wave_rub_up_down", "wave_rub_front_back", "static_rub_front_back",'''
    content = content.replace(sync_old, sync_new)

    # Add kinematics block
    new_mode_block = '''
            elif self.motion_mode == "static_rub_front_back":
                # Static front-back rubbing (原地前后波浪形揉搓)
                # No vertical movement. R2 (Pitch) pitches the toe/heel against the shaft.
                pos_l0 = center_l0
                pos_a_l2 = center_l2
                pos_b_l2 = center_l2

                # R2 pitches dynamically to wipe front/back
                pos_a_r2 = center_r2 + amp_r2 * math.cos(phase_a)
                pos_b_r2 = center_r2 - amp_r2 * math.cos(phase_a) # Mirror pitch

                cmd_a_parts.extend([f"L0{clamp(pos_l0):04d}", f"L2{clamp(pos_a_l2):04d}", f"R2{clamp(pos_a_r2):04d}", f"R1{clamp(center_r1):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_l0):04d}", f"L2{clamp(pos_b_l2):04d}", f"R2{clamp(pos_b_r2):04d}", f"R1{clamp(center_r1):04d}"])
'''
    target = '            elif self.motion_mode == "alternating_step":'
    content = content.replace(target, new_mode_block + target)

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
