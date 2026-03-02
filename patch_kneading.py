import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # The user wants "dynamic kneading" (动态揉捏).
    # Since the heel-to-toe line is perpendicular to the penis, the sole is gripping it like a horizontal clamp.
    # To "knead" or "massage" (揉捏), the foot needs to roll/tilt along the penis or squeeze tightly and release.
    # In SR6, R1 (Roll) twists the foot along the long axis of the device. If the device is pointed 45 deg down at the penis,
    # rolling the foot will tilt the arch up/down along the shaft, creating a rubbing/rolling massage sensation!
    # R2 (Pitch) tilts the toe/heel, which in this perpendicular orientation, would pivot the foot horizontally around the penis,
    # sweeping the toe and heel back and forth (like a wiping motion).
    # Both are good for kneading! We should re-introduce the dynamic R1/R2 to `v_stroke` and `alternating_step`,
    # but based on the `pitch_amp` and `roll_amp` user controls.

    v_stroke_old = '''            if self.motion_mode == "v_stroke":
                # Devices are at 45 deg facing center.
                # Kinematic Inverse: To stroke perfectly along the central Z-axis (shaft):
                # When L0 extends (sin -> +1), it moves inward and forward.
                # We MUST retract L2 outward to keep the gap constant.
                # Since 45 deg, sin(45)=cos(45)=0.707. L0 extension = L2 outward compensation.
                # Standard L2: 5000 center, <5000 Left, >5000 Right.
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

    v_stroke_new = '''            if self.motion_mode == "v_stroke":
                # Arch grip: Heel-to-toe is perpendicular to the shaft.
                # L0 extends diagonally; L2 compensates to keep the feet sliding strictly parallel to the shaft.
                z_motion = amp_l0 * math.sin(phase_a)
                pos_l0 = center_l0 + z_motion

                # Compensate laterally (L2) to maintain grip pressure while stroking
                pos_a_l2 = center_l2 - z_motion
                pos_b_l2 = center_l2 + z_motion

                # Dynamic Kneading (动态揉捏):
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

    content = content.replace(v_stroke_old, v_stroke_new)

    alt_step_old = '''            elif self.motion_mode == "alternating_step":
                # Same parallel kinematics as v_stroke, but alternating phases
                z_motion_a = amp_l0 * math.sin(phase_a)
                z_motion_b = amp_l0 * math.sin(phase_b)

                pos_a_l0 = center_l0 + z_motion_a
                pos_b_l0 = center_l0 + z_motion_b

                # Compensate laterally to keep parallel to central Z axis
                pos_a_l2 = center_l2 - z_motion_a # A moves Left (outward)
                pos_b_l2 = center_l2 + z_motion_b # B moves Right (outward)

                pos_r2 = center_r2 # Keep ankle angle fixed for parallel stroking

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"L2{clamp(pos_a_l2):04d}", f"R2{clamp(pos_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"L2{clamp(pos_b_l2):04d}", f"R2{clamp(pos_r2):04d}"])'''

    alt_step_new = '''            elif self.motion_mode == "alternating_step":
                # Alternating strokes with parallel L2 compensation
                z_motion_a = amp_l0 * math.sin(phase_a)
                z_motion_b = amp_l0 * math.sin(phase_b)

                pos_a_l0 = center_l0 + z_motion_a
                pos_b_l0 = center_l0 + z_motion_b

                pos_a_l2 = center_l2 - z_motion_a
                pos_b_l2 = center_l2 + z_motion_b

                # Dynamic Alternating Kneading
                pos_a_r2 = center_r2 + amp_r2 * math.cos(phase_a)
                pos_b_r2 = center_r2 - amp_r2 * math.cos(phase_b)

                pos_a_r1 = center_rx + amp_r1 * math.sin(phase_a)
                pos_b_r1 = center_rx - amp_r1 * math.sin(phase_b)

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"L2{clamp(pos_a_l2):04d}", f"R2{clamp(pos_a_r2):04d}", f"R1{clamp(pos_a_r1):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"L2{clamp(pos_b_l2):04d}", f"R2{clamp(pos_b_r2):04d}", f"R1{clamp(pos_b_r1):04d}"])'''

    content = content.replace(alt_step_old, alt_step_new)

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
print("Dynamic Kneading added")
