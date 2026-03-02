import re

def update_kinematics():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # Step 1: Add L1 amplitude to the amplitudes section
    if "amp_l1" not in content:
        content = content.replace(
            "amp_l0 = (self.stroke / 100.0) * 5000",
            "amp_l0 = (self.stroke / 100.0) * 5000\n            amp_l1 = amp_l0  # 45 deg geometry means L1 compensation is 1:1 with L0"
        )

    if "center_l1" not in content:
        content = content.replace(
            "center_l0 = (self.base_squeeze / 100.0) * 9999",
            "center_l0 = (self.base_squeeze / 100.0) * 9999\n            center_l1 = 5000"
        )

    # Step 2: Replace v_stroke logic
    v_stroke_old = '''            if self.motion_mode == "v_stroke":
                # Devices are at 45 deg facing center.
                # L0 pushing out moves feet inwards & forwards.
                # To keep soles parallel to the center axis, pitch (R2) must tilt toes "up" (relative to the device).
                # Assuming R2=9999 is pitch up, and R2=0000 is pitch down.
                pos_l0 = center_l0 + amp_l0 * math.sin(phase_a)

                # Active pitch compensation: when L0 extends (sin -> +1), R2 pitches UP to compensate for the 45deg downward slope.
                # Use pitch_amp to control the *intensity* of this compensation.
                pos_a_r2 = center_r2 + amp_r2 * math.sin(phase_a)
                pos_b_r2 = center_r2 + amp_r2 * math.sin(phase_a) # Symmetric

                cmd_a_parts.extend([f"L0{clamp(pos_l0):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_l0):04d}", f"R2{clamp(pos_b_r2):04d}"])'''

    v_stroke_new = '''            if self.motion_mode == "v_stroke":
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

                pos_a_l1 = center_l1 - z_motion # Device A moves Left (outward)
                pos_b_l1 = center_l1 + z_motion # Device B moves Right (outward)

                # Pitch (R2) stays constant relative to device base, parallel to shaft.
                pos_r2 = center_r2 # Controlled by ankle_angle_offset UI

                cmd_a_parts.extend([f"L0{clamp(pos_l0):04d}", f"L1{clamp(pos_a_l1):04d}", f"R2{clamp(pos_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_l0):04d}", f"L1{clamp(pos_b_l1):04d}", f"R2{clamp(pos_r2):04d}"])'''

    content = content.replace(v_stroke_old, v_stroke_new)


    # Step 3: Replace alternating_step logic
    alt_step_old = '''            elif self.motion_mode == "alternating_step":
                # Left foot pushes in (L0) and points toe down (R2 down, e.g. -R2).
                # Right foot pulls out (L0) and points toe up (R2 up, e.g. +R2).
                pos_a_l0 = center_l0 + amp_l0 * math.sin(phase_a)
                pos_b_l0 = center_l0 + amp_l0 * math.sin(phase_b)

                # When L0 pushes (sin -> +1), R2 pitches down (cos or -sin -> -1).
                # We use -sin so it's in phase with the stroke: push out -> toe down.
                pos_a_r2 = center_r2 - amp_r2 * math.sin(phase_a)
                pos_b_r2 = center_r2 - amp_r2 * math.sin(phase_b)

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"R2{clamp(pos_b_r2):04d}"])'''

    alt_step_new = '''            elif self.motion_mode == "alternating_step":
                # Same parallel kinematics as v_stroke, but alternating phases
                z_motion_a = amp_l0 * math.sin(phase_a)
                z_motion_b = amp_l0 * math.sin(phase_b)

                pos_a_l0 = center_l0 + z_motion_a
                pos_b_l0 = center_l0 + z_motion_b

                # Compensate laterally to keep parallel to central Z axis
                pos_a_l1 = center_l1 - z_motion_a # A moves Left (outward)
                pos_b_l1 = center_l1 + z_motion_b # B moves Right (outward)

                pos_r2 = center_r2 # Keep ankle angle fixed for parallel stroking

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"L1{clamp(pos_a_l1):04d}", f"R2{clamp(pos_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"L1{clamp(pos_b_l1):04d}", f"R2{clamp(pos_r2):04d}"])'''

    content = content.replace(alt_step_old, alt_step_new)

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

update_kinematics()
print("Kinematics patched!")
