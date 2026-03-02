import re

with open('dual_osr_control.py', 'r') as f:
    content = f.read()

# Replace the motion loop logic to include single foot modes
old_loop = """            elif self.motion_mode == "circling_tease":
                # Feet held gently on the target.
                # Roll (R1) and Pitch (R2) move in a circular sine/cosine pattern to create a grinding orbital motion.
                pos_a_r1 = center_rx + amp_r1 * math.sin(phase_a)
                pos_b_r1 = center_rx - amp_r1 * math.sin(phase_a) # mirror roll

                pos_a_r2 = center_r2 + amp_r2 * math.cos(phase_a)
                pos_b_r2 = center_r2 + amp_r2 * math.cos(phase_a) # sync pitch

                cmd_a_parts.extend([f"L0{clamp(center_l0):04d}", f"R1{clamp(pos_a_r1):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(center_l0):04d}", f"R1{clamp(pos_b_r1):04d}", f"R2{clamp(pos_b_r2):04d}"])

            else: # fallback"""

new_loop = """            elif self.motion_mode == "circling_tease":
                # Feet held gently on the target.
                # Roll (R1) and Pitch (R2) move in a circular sine/cosine pattern to create a grinding orbital motion.
                pos_a_r1 = center_rx + amp_r1 * math.sin(phase_a)
                pos_b_r1 = center_rx - amp_r1 * math.sin(phase_a) # mirror roll

                pos_a_r2 = center_r2 + amp_r2 * math.cos(phase_a)
                pos_b_r2 = center_r2 + amp_r2 * math.cos(phase_a) # sync pitch

                cmd_a_parts.extend([f"L0{clamp(center_l0):04d}", f"R1{clamp(pos_a_r1):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(center_l0):04d}", f"R1{clamp(pos_b_r1):04d}", f"R2{clamp(pos_b_r2):04d}"])

            elif self.motion_mode == "single_foot_tease_left":
                # Left foot teases with rapid flickering pitch, Right foot stays still at base squeeze
                fast_phase_a = phase_a * 2.0

                # Active Left (Device A)
                pos_a_r2 = center_r2 - (amp_r2 / 2.0) - (amp_r2 / 2.0) * math.sin(fast_phase_a)
                pos_a_l0 = center_l0 + (amp_l0 * 0.1) * math.sin(phase_a)

                # Static Right (Device B)
                pos_b_r2 = center_r2
                pos_b_l0 = center_l0

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"R2{clamp(pos_b_r2):04d}"])

            elif self.motion_mode == "single_foot_tease_right":
                # Right foot teases with rapid flickering pitch, Left foot stays still at base squeeze
                fast_phase_b = phase_a * 2.0 # phase_a is fine here since it's isolated

                # Static Left (Device A)
                pos_a_r2 = center_r2
                pos_a_l0 = center_l0

                # Active Right (Device B)
                pos_b_r2 = center_r2 - (amp_r2 / 2.0) - (amp_r2 / 2.0) * math.sin(fast_phase_b)
                pos_b_l0 = center_l0 + (amp_l0 * 0.1) * math.sin(phase_a)

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"R2{clamp(pos_b_r2):04d}"])

            elif self.motion_mode == "single_foot_stroke_left":
                # Left foot strokes with pitch compensation, Right foot holds still
                pos_a_l0 = center_l0 + amp_l0 * math.sin(phase_a)
                pos_a_r2 = center_r2 + amp_r2 * math.sin(phase_a)

                pos_b_l0 = center_l0
                pos_b_r2 = center_r2

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"R2{clamp(pos_b_r2):04d}"])

            elif self.motion_mode == "single_foot_stroke_right":
                # Right foot strokes with pitch compensation, Left foot holds still
                pos_a_l0 = center_l0
                pos_a_r2 = center_r2

                pos_b_l0 = center_l0 + amp_l0 * math.sin(phase_a) # Use phase_a for the active foot
                pos_b_r2 = center_r2 + amp_r2 * math.sin(phase_a)

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"R2{clamp(pos_b_r2):04d}"])

            else: # fallback"""

content = content.replace(old_loop, new_loop)

# Update phase shift logic for the new single-foot modes
old_update = """        # In some modes, we want synchronous base loops
        if mode in ["v_stroke", "wrapping_twist", "sole_rub", "edge_stroking", "heel_press", "circling_tease", "toe_tease"]:
            self.controller.phase_shift = 0   # Base phase sync (modes handle mirroring internally if needed)
        else:
            self.controller.phase_shift = 180 # Base phase alternating (e.g. alternating_step)"""

new_update = """        # In some modes, we want synchronous base loops
        if mode in ["v_stroke", "wrapping_twist", "sole_rub", "edge_stroking", "heel_press", "circling_tease", "toe_tease",
                    "single_foot_tease_left", "single_foot_tease_right", "single_foot_stroke_left", "single_foot_stroke_right"]:
            self.controller.phase_shift = 0   # Base phase sync (modes handle mirroring internally if needed)
        else:
            self.controller.phase_shift = 180 # Base phase alternating (e.g. alternating_step)"""

content = content.replace(old_update, new_update)

with open('dual_osr_control.py', 'w') as f:
    f.write(content)
