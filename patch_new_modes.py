import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # 1. Add modes to UI list
    ui_old = '''        modes = [
            "v_stroke", "alternating_step", "wrapping_twist", "sole_rub",
            "toe_tease", "edge_stroking", "heel_press", "circling_tease",
            "single_foot_tease_left", "single_foot_tease_right",
            "single_foot_stroke_left", "single_foot_stroke_right"
        ]'''

    ui_new = '''        modes = [
            "v_stroke", "alternating_step", "wrapping_twist", "sole_rub",
            "toe_tease", "edge_stroking", "heel_press", "circling_tease",
            "wave_rub_up_down", "wave_rub_front_back",
            "single_foot_tease_left", "single_foot_tease_right",
            "single_foot_stroke_left", "single_foot_stroke_right"
        ]'''
    content = content.replace(ui_old, ui_new)

    # 2. Add to phase sync list
    sync_old = '''        if mode in ["v_stroke", "wrapping_twist", "sole_rub", "edge_stroking", "heel_press", "circling_tease", "toe_tease",
                    "single_foot_tease_left", "single_foot_tease_right", "single_foot_stroke_left", "single_foot_stroke_right"]:'''
    sync_new = '''        if mode in ["v_stroke", "wrapping_twist", "sole_rub", "edge_stroking", "heel_press", "circling_tease", "toe_tease",
                    "wave_rub_up_down", "wave_rub_front_back",
                    "single_foot_tease_left", "single_foot_tease_right", "single_foot_stroke_left", "single_foot_stroke_right"]:'''
    content = content.replace(sync_old, sync_new)

    # 3. Simplify v_stroke to pure parallel sliding
    v_stroke_old = '''            if self.motion_mode == "v_stroke":
                # Arch grip: Heel-to-toe is perpendicular to the shaft.
                # L0 extends diagonally; L2 compensates to keep the feet sliding strictly parallel to the shaft.
                z_motion = amp_l0 * math.sin(phase_a)
                pos_l0 = center_l0 + z_motion

                # Compensate laterally (L2) to maintain grip pressure while stroking
                pos_a_l2 = center_l2 - (z_motion * l2_mult)
                pos_b_l2 = center_l2 + (z_motion * l2_mult)

                # Dynamic Kneading:
                # User requested a kneading motion while stroking.
                # R2 (Pitch) wags the toe/heel back and forth (wiping).
                # R1 (Roll) tilts the arch up and down the shaft (rolling massage).
                # We apply the amplitudes set in the UI, slightly out of phase (cos) to create an elliptical massage.
                pos_a_r2 = center_r2 + amp_r2 * math.cos(phase_a)
                pos_b_r2 = center_r2 - amp_r2 * math.cos(phase_a) # Mirror pitch for symmetric kneading

                pos_a_r1 = center_rx + amp_r1 * math.sin(phase_a)
                pos_b_r1 = center_rx - amp_r1 * math.sin(phase_a)

                cmd_a_parts.extend([f"L0{clamp(pos_l0):04d}", f"L2{clamp(pos_a_l2):04d}", f"R2{clamp(pos_a_r2):04d}", f"R1{clamp(pos_a_r1):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_l0):04d}", f"L2{clamp(pos_b_l2):04d}", f"R2{clamp(pos_b_r2):04d}", f"R1{clamp(pos_b_r1):04d}"])'''

    v_stroke_new = '''            if self.motion_mode == "v_stroke":
                # Pure parallel sliding stroke
                z_motion = amp_l0 * math.sin(phase_a)
                pos_l0 = center_l0 + z_motion

                # Compensate laterally (L2) to maintain grip pressure while stroking
                pos_a_l2 = center_l2 - (z_motion * l2_mult)
                pos_b_l2 = center_l2 + (z_motion * l2_mult)

                cmd_a_parts.extend([f"L0{clamp(pos_l0):04d}", f"L2{clamp(pos_a_l2):04d}", f"R2{clamp(center_r2):04d}", f"R1{clamp(center_rx):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_l0):04d}", f"L2{clamp(pos_b_l2):04d}", f"R2{clamp(center_r2):04d}", f"R1{clamp(center_rx):04d}"])'''
    content = content.replace(v_stroke_old, v_stroke_new)

    # 4. Inject new modes right after v_stroke
    wave_modes = '''
            elif self.motion_mode == "wave_rub_up_down":
                # Up-down wave rubbing (上下波浪形揉搓)
                # Parallel sliding stroke with R1 (Roll) rolling the arch up and down the shaft
                z_motion = amp_l0 * math.sin(phase_a)
                pos_l0 = center_l0 + z_motion

                pos_a_l2 = center_l2 - (z_motion * l2_mult)
                pos_b_l2 = center_l2 + (z_motion * l2_mult)

                # R1 rolls dynamically out of phase with the stroke to create a massaging wave
                pos_a_r1 = center_rx + amp_r1 * math.cos(phase_a)
                pos_b_r1 = center_rx - amp_r1 * math.cos(phase_a) # Mirror roll

                cmd_a_parts.extend([f"L0{clamp(pos_l0):04d}", f"L2{clamp(pos_a_l2):04d}", f"R2{clamp(center_r2):04d}", f"R1{clamp(pos_a_r1):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_l0):04d}", f"L2{clamp(pos_b_l2):04d}", f"R2{clamp(center_r2):04d}", f"R1{clamp(pos_b_r1):04d}"])

            elif self.motion_mode == "wave_rub_front_back":
                # Front-back wave rubbing (前后波浪形揉搓)
                # Parallel sliding stroke with R2 (Pitch) pitching the toe/heel against the shaft
                z_motion = amp_l0 * math.sin(phase_a)
                pos_l0 = center_l0 + z_motion

                pos_a_l2 = center_l2 - (z_motion * l2_mult)
                pos_b_l2 = center_l2 + (z_motion * l2_mult)

                # R2 pitches dynamically to wipe front/back
                pos_a_r2 = center_r2 + amp_r2 * math.cos(phase_a)
                pos_b_r2 = center_r2 - amp_r2 * math.cos(phase_a) # Mirror pitch

                cmd_a_parts.extend([f"L0{clamp(pos_l0):04d}", f"L2{clamp(pos_a_l2):04d}", f"R2{clamp(pos_a_r2):04d}", f"R1{clamp(center_rx):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_l0):04d}", f"L2{clamp(pos_b_l2):04d}", f"R2{clamp(pos_b_r2):04d}", f"R1{clamp(center_rx):04d}"])
'''
    content = content.replace('            elif self.motion_mode == "alternating_step":', wave_modes + '            elif self.motion_mode == "alternating_step":')

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
print("New modes added")
