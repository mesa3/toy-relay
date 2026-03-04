import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # 1. Add to UI
    ui_old = '''            "foot_slap", "glans_torture",'''
    ui_new = '''            "foot_slap", "glans_torture", "edging_sole_show",'''
    content = content.replace(ui_old, ui_new)

    # 2. Add to sync list
    sync_old = '''                    "wave_rub_front_back", "static_rub_front_back", "asymmetric_sprint", "foot_slap", "glans_torture",'''
    sync_new = '''                    "wave_rub_front_back", "static_rub_front_back", "asymmetric_sprint", "foot_slap", "glans_torture", "edging_sole_show",'''
    content = content.replace(sync_old, sync_new)

    # 3. Inject logic
    new_mode_block = '''
            elif self.motion_mode == "edging_sole_show":
                # Edging Sole Show (寸止展示脚底)
                # Fast strokes followed by a sudden stop, pulling back, spreading wide, and pitching up to show soles.

                # Director phase: slow cycle to toggle between stroking and showing
                # Let's say 1 full director cycle = 5 fast stroke cycles.
                # Director > 0 (stroking phase), Director < 0 (show phase)
                director = math.sin(phase_a * 0.2)
                fast_phase = phase_a * 2.0

                if director > 0:
                    # Stroking Phase (Fast parallel v_stroke)
                    # We add a smooth transition based on the director sine to avoid harsh snaps,
                    # but for now a direct cut is fine since they are T-code commands.
                    z_motion = amp_l0 * math.sin(fast_phase)

                    pos_l0 = center_l0 + z_motion
                    pos_a_l2 = center_l2 - (z_motion * l2_mult)
                    pos_b_l2 = center_l2 + (z_motion * l2_mult)

                    # Normal pitch and roll
                    pos_a_r2 = center_r2
                    pos_b_r2 = center_r2
                    pos_a_r1 = center_a_r1
                    pos_b_r1 = center_b_r1

                else:
                    # Show Phase (Pulled back, spread open, soles pitched up)
                    # Pull L0 all the way back
                    pos_l0 = center_l0 - amp_l0

                    # Spread L2 wide (outward)
                    # L2 moving outward: A moves left (subtract), B moves right (add)
                    pos_a_l2 = center_l2 - (amp_l0 * l2_mult)
                    pos_b_l2 = center_l2 + (amp_l0 * l2_mult)

                    # Pitch (R2) heavily up to expose sole
                    pos_a_r2 = center_r2 + amp_r2
                    pos_b_r2 = center_r2 + amp_r2

                    # Roll (R1) optional, let's keep it flat or slight inward
                    pos_a_r1 = center_a_r1
                    pos_b_r1 = center_b_r1

                cmd_a_parts.extend([f"L0{clamp(pos_l0):04d}", f"L2{clamp(pos_a_l2):04d}", f"R2{clamp(pos_a_r2):04d}", f"R1{clamp(pos_a_r1):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_l0):04d}", f"L2{clamp(pos_b_l2):04d}", f"R2{clamp(pos_b_r2):04d}", f"R1{clamp(pos_b_r1):04d}"])
'''
    target = '            elif self.motion_mode == "single_foot_tease_left":'
    content = content.replace(target, new_mode_block + target)

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
print("Edging mode added")
