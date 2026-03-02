def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # We need to completely replace the v_stroke section.
    # The current v_stroke section starts at `if self.motion_mode == "v_stroke":`
    # and ends before `elif self.motion_mode == "alternating_step":`

    old_section = '''            if self.motion_mode == "v_stroke":
                # Devices are at 45 deg facing center.
                # Kinematic Inverse: To stroke perfectly along the central Z-axis (shaft):
                # When L0 extends (sin -> +1), it moves inward and forward.
                # We MUST retract L1 outward to keep the gap constant.
                # Since 45 deg, sin(45)=cos(45)=0.707. L0 extension = L1 outward compensation.
                # Standard L1: 5000 center, <5000 Left, >5000 Right.
                # Device A (Left): extend pushes Right. Compensate by moving Left (-).
                # Device B (Right): extend pushes Left. Compensate by moving Right (+).
                z_motion = amp_l0 * math.sin(phase_a)
                pos_l0 = center_l0 + z_motion

                pos_a_l2 = center_l2 - z_motion # Device A moves Left (outward)
                pos_b_l2 = center_l2 + z_motion # Device B moves Right (outward)

                # Pitch (R2) stays constant relative to device base, parallel to shaft.
                pos_r2 = center_r2 # Controlled by ankle_angle_offset UI

                cmd_a_parts.extend([f"L0{clamp(pos_l0):04d}", f"L2{clamp(pos_a_l2):04d}", f"R2{clamp(pos_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_l0):04d}", f"L2{clamp(pos_b_l2):04d}", f"R2{clamp(pos_r2):04d}"])'''

    new_section = '''            if self.motion_mode == "v_stroke":
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

    if old_section in content:
        content = content.replace(old_section, new_section)
        with open('dual_osr_control.py', 'w') as f:
            f.write(content)
        print("Patched v_stroke successfully.")
    else:
        print("Error: Could not find old_section in dual_osr_control.py")

patch()
