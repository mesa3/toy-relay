import re

with open('dual_osr_control.py', 'r') as f:
    content = f.read()

# Replace the modes list in the init
old_init = """        self.base_squeeze = 50.0 # Base L0 offset
        self.motion_mode = "walk"
"""
new_init = """        self.base_squeeze = 50.0 # Base L0 offset
        self.motion_mode = "v_stroke"
"""
content = content.replace(old_init, new_init)

# Replace the motion loop logic
old_loop = """            if self.motion_mode == "walk":
                pos_a = center_l0 + amp_l0 * math.sin(phase_a)
                pos_b = center_l0 + amp_l0 * math.sin(phase_b)
                cmd_a_parts.append(f"L0{int(pos_a):04d}")
                cmd_b_parts.append(f"L0{int(pos_b):04d}")

            elif self.motion_mode == "squeeze_rub":
                # Sync L0 squeeze, alternating R2 pitch
                pos_l0 = center_l0 + amp_l0 * math.sin(phase_a)
                pos_a_r2 = center_rx + amp_r2 * math.sin(phase_a)
                pos_b_r2 = center_rx + amp_r2 * math.sin(phase_b)

                cmd_a_parts.extend([f"L0{int(pos_l0):04d}", f"R2{int(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{int(pos_l0):04d}", f"R2{int(pos_b_r2):04d}"])

            elif self.motion_mode == "ankle_massage":
                # Hold L0 squeeze, alternating R1 roll
                pos_a_r1 = center_rx + amp_r1 * math.sin(phase_a)
                pos_b_r1 = center_rx + amp_r1 * math.sin(phase_b)

                cmd_a_parts.extend([f"L0{int(center_l0):04d}", f"R1{int(pos_a_r1):04d}"])
                cmd_b_parts.extend([f"L0{int(center_l0):04d}", f"R1{int(pos_b_r1):04d}"])

            elif self.motion_mode == "stepping":
                # Alternating L0 and Alternating R2 (pitching down while stepping)
                pos_a_l0 = center_l0 + amp_l0 * math.sin(phase_a)
                pos_b_l0 = center_l0 + amp_l0 * math.sin(phase_b)

                # Pitch correlates with stroke (toe points down when pushing out)
                pos_a_r2 = center_rx + amp_r2 * math.cos(phase_a)
                pos_b_r2 = center_rx + amp_r2 * math.cos(phase_b)

                cmd_a_parts.extend([f"L0{int(pos_a_l0):04d}", f"R2{int(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{int(pos_b_l0):04d}", f"R2{int(pos_b_r2):04d}"])

            elif self.motion_mode == "twisting":
                # Alternating R0 twist and R1 roll, gentle L0 sync
                pos_l0 = center_l0 + (amp_l0 * 0.5) * math.sin(phase_a)

                pos_a_r0 = center_rx + amp_r0 * math.sin(phase_a)
                pos_b_r0 = center_rx + amp_r0 * math.sin(phase_b)

                pos_a_r1 = center_rx + amp_r1 * math.cos(phase_a)
                pos_b_r1 = center_rx + amp_r1 * math.cos(phase_b)

                cmd_a_parts.extend([f"L0{int(pos_l0):04d}", f"R0{int(pos_a_r0):04d}", f"R1{int(pos_a_r1):04d}"])
                cmd_b_parts.extend([f"L0{int(pos_l0):04d}", f"R0{int(pos_b_r0):04d}", f"R1{int(pos_b_r1):04d}"])

            else:
                pos_a = center_l0 + amp_l0 * math.sin(phase_a)
                pos_b = center_l0 + amp_l0 * math.sin(phase_b)
                cmd_a_parts.append(f"L0{int(pos_a):04d}")
                cmd_b_parts.append(f"L0{int(pos_b):04d}")"""

new_loop = """            if self.motion_mode == "v_stroke":
                # Devices are at 45 deg facing center.
                # L0 pushing out moves feet inwards & forwards.
                # To keep soles parallel to the center axis, pitch (R2) must tilt toes "up" (relative to the device).
                # Assuming R2=9999 is pitch up, and R2=0000 is pitch down.
                pos_l0 = center_l0 + amp_l0 * math.sin(phase_a)

                # Active pitch compensation: when L0 extends (sin -> +1), R2 pitches UP to compensate for the 45deg downward slope.
                # Use pitch_amp to control the *intensity* of this compensation.
                pos_a_r2 = center_rx + amp_r2 * math.sin(phase_a)
                pos_b_r2 = center_rx + amp_r2 * math.sin(phase_a) # Symmetric

                cmd_a_parts.extend([f"L0{int(pos_l0):04d}", f"R2{int(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{int(pos_l0):04d}", f"R2{int(pos_b_r2):04d}"])

            elif self.motion_mode == "alternating_step":
                # Left foot pushes in (L0) and points toe down (R2 down, e.g. -R2).
                # Right foot pulls out (L0) and points toe up (R2 up, e.g. +R2).
                pos_a_l0 = center_l0 + amp_l0 * math.sin(phase_a)
                pos_b_l0 = center_l0 + amp_l0 * math.sin(phase_b)

                # When L0 pushes (sin -> +1), R2 pitches down (cos or -sin -> -1).
                # We use -sin so it's in phase with the stroke: push out -> toe down.
                pos_a_r2 = center_rx - amp_r2 * math.sin(phase_a)
                pos_b_r2 = center_rx - amp_r2 * math.sin(phase_b)

                cmd_a_parts.extend([f"L0{int(pos_a_l0):04d}", f"R2{int(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{int(pos_b_l0):04d}", f"R2{int(pos_b_r2):04d}"])

            elif self.motion_mode == "wrapping_twist":
                # Hold a constant close squeeze (L0).
                # Roll soles inwards (R1). Assuming +R1 is roll inwards for left foot, then -R1 is inwards for right foot.
                # (Or vice versa, they should be out of phase to roll symmetrically relative to the center).
                pos_a_r1 = center_rx + amp_r1 * math.sin(phase_a)
                pos_b_r1 = center_rx - amp_r1 * math.sin(phase_a) # Mirror roll inwards

                # Alternate twisting to rub the sides (R0)
                pos_a_r0 = center_rx + amp_r0 * math.cos(phase_a)
                pos_b_r0 = center_rx + amp_r0 * math.cos(phase_b) # Alternating twist

                cmd_a_parts.extend([f"L0{int(center_l0):04d}", f"R1{int(pos_a_r1):04d}", f"R0{int(pos_a_r0):04d}"])
                cmd_b_parts.extend([f"L0{int(center_l0):04d}", f"R1{int(pos_b_r1):04d}", f"R0{int(pos_b_r0):04d}"])

            elif self.motion_mode == "sole_rub":
                # Gentle constant L0 base squeeze.
                # Alternate Pitch (R2) and Roll (R1) to "knead" with the soles.
                # Left toe goes up and rolls in, Right toe goes down and rolls out.
                pos_a_r2 = center_rx + amp_r2 * math.sin(phase_a)
                pos_b_r2 = center_rx + amp_r2 * math.sin(phase_b)

                # Adding Roll out of phase for a circular grinding motion
                pos_a_r1 = center_rx + amp_r1 * math.cos(phase_a)
                pos_b_r1 = center_rx + amp_r1 * math.cos(phase_b)

                cmd_a_parts.extend([f"L0{int(center_l0):04d}", f"R2{int(pos_a_r2):04d}", f"R1{int(pos_a_r1):04d}"])
                cmd_b_parts.extend([f"L0{int(center_l0):04d}", f"R2{int(pos_b_r2):04d}", f"R1{int(pos_b_r1):04d}"])

            else: # fallback
                pos_a = center_l0 + amp_l0 * math.sin(phase_a)
                pos_b = center_l0 + amp_l0 * math.sin(phase_b)
                cmd_a_parts.append(f"L0{int(pos_a):04d}")
                cmd_b_parts.append(f"L0{int(pos_b):04d}")"""

content = content.replace(old_loop, new_loop)

# Fix phase handling in update_params
old_update = """        # In twisting or squeeze mode, they often operate in sync or have specialized phase handling
        if mode == "squeeze_rub":
            self.controller.phase_shift = 0  # Sync L0
        else:
            self.controller.phase_shift = 180 # Alternating L0"""
new_update = """        # In some modes, we want synchronous base loops
        if mode in ["v_stroke", "wrapping_twist", "sole_rub"]:
            self.controller.phase_shift = 0   # Base phase sync (modes handle mirroring internally if needed)
        else:
            self.controller.phase_shift = 180 # Base phase alternating (e.g. alternating_step)"""

content = content.replace(old_update, new_update)

with open('dual_osr_control.py', 'w') as f:
    f.write(content)
