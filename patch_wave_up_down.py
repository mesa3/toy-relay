import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # 1. Fix the update_params phase list
    old_sync = '''        if mode in ["v_stroke", "wrapping_twist", "sole_rub", "edge_stroking", "heel_press", "circling_tease", "toe_tease",
                    "wave_rub_up_down", "wave_rub_front_back", "static_rub_front_back", "asymmetric_sprint", "static_rub_front_back",
                    "single_foot_tease_left", "single_foot_tease_right", "single_foot_stroke_left", "single_foot_stroke_right"]:'''

    new_sync = '''        if mode in ["v_stroke", "wrapping_twist", "sole_rub", "edge_stroking", "heel_press", "circling_tease", "toe_tease",
                    "wave_rub_front_back", "static_rub_front_back", "asymmetric_sprint",
                    "single_foot_tease_left", "single_foot_tease_right", "single_foot_stroke_left", "single_foot_stroke_right"]:'''
    content = content.replace(old_sync, new_sync)

    # 2. Fix the wave_rub_up_down logic in motion_loop
    old_logic = '''            elif self.motion_mode == "wave_rub_up_down":
                # Up-down wave rubbing (上下波浪形揉搓)
                # Parallel sliding stroke with R1 (Roll) rolling the arch up and down the shaft
                z_motion = amp_l0 * math.sin(phase_a)
                pos_l0 = center_l0 + z_motion

                pos_a_l2 = center_l2 - (z_motion * l2_mult)
                pos_b_l2 = center_l2 + (z_motion * l2_mult)

                # R1 rolls dynamically out of phase with the stroke to create a massaging wave
                pos_a_r1 = center_a_r1 + amp_r1 * math.cos(phase_a)
                pos_b_r1 = center_b_r1 + amp_r1 * math.cos(phase_a) # Alternating phase (+ instead of -)

                cmd_a_parts.extend([f"L0{clamp(pos_l0):04d}", f"L2{clamp(pos_a_l2):04d}", f"R2{clamp(center_r2):04d}", f"R1{clamp(pos_a_r1):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_l0):04d}", f"L2{clamp(pos_b_l2):04d}", f"R2{clamp(center_r2):04d}", f"R1{clamp(pos_b_r1):04d}"])'''

    new_logic = '''            elif self.motion_mode == "wave_rub_up_down":
                # Up-down wave rubbing (上下波浪形揉搓)
                # Alternating vertical strokes with R1 rolling the arch up and down the shaft
                z_motion_a = amp_l0 * math.sin(phase_a)
                z_motion_b = amp_l0 * math.sin(phase_b) # phase_b is 180 deg out because it's no longer in sync list

                pos_a_l0 = center_l0 + z_motion_a
                pos_b_l0 = center_l0 + z_motion_b

                pos_a_l2 = center_l2 - (z_motion_a * l2_mult)
                pos_b_l2 = center_l2 + (z_motion_b * l2_mult)

                # R1 rolls dynamically out of phase with the stroke to create a massaging wave
                # Using standard minus mirror for B + phase_b naturally achieves the physical alternating roll
                pos_a_r1 = center_a_r1 + amp_r1 * math.cos(phase_a)
                pos_b_r1 = center_b_r1 - amp_r1 * math.cos(phase_b)

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"L2{clamp(pos_a_l2):04d}", f"R2{clamp(center_r2):04d}", f"R1{clamp(pos_a_r1):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"L2{clamp(pos_b_l2):04d}", f"R2{clamp(center_r2):04d}", f"R1{clamp(pos_b_r1):04d}"])'''

    content = content.replace(old_logic, new_logic)

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
print("Updated wave_rub_up_down to alternating")
