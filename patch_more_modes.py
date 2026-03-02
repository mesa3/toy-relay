import re

with open('dual_osr_control.py', 'r') as f:
    content = f.read()

# Replace the motion loop logic
old_loop = """            elif self.motion_mode == "sole_rub":
                # Gentle constant L0 base squeeze.
                # Alternate Pitch (R2) and Roll (R1) to "knead" with the soles.
                # Left toe goes up and rolls in, Right toe goes down and rolls out.
                pos_a_r2 = center_rx + amp_r2 * math.sin(phase_a)
                pos_b_r2 = center_rx + amp_r2 * math.sin(phase_b)

                # Adding Roll out of phase for a circular grinding motion
                pos_a_r1 = center_rx + amp_r1 * math.cos(phase_a)
                pos_b_r1 = center_rx + amp_r1 * math.cos(phase_b)

                cmd_a_parts.extend([f"L0{clamp(center_l0):04d}", f"R2{clamp(pos_a_r2):04d}", f"R1{clamp(pos_a_r1):04d}"])
                cmd_b_parts.extend([f"L0{clamp(center_l0):04d}", f"R2{clamp(pos_b_r2):04d}", f"R1{clamp(pos_b_r1):04d}"])

            else: # fallback
                pos_a = center_l0 + amp_l0 * math.sin(phase_a)
                pos_b = center_l0 + amp_l0 * math.sin(phase_b)
                cmd_a_parts.append(f"L0{clamp(pos_a):04d}")
                cmd_b_parts.append(f"L0{clamp(pos_b):04d}")"""

new_loop = """            elif self.motion_mode == "sole_rub":
                pos_a_r2 = center_rx + amp_r2 * math.sin(phase_a)
                pos_b_r2 = center_rx + amp_r2 * math.sin(phase_b)

                pos_a_r1 = center_rx + amp_r1 * math.cos(phase_a)
                pos_b_r1 = center_rx + amp_r1 * math.cos(phase_b)

                cmd_a_parts.extend([f"L0{clamp(center_l0):04d}", f"R2{clamp(pos_a_r2):04d}", f"R1{clamp(pos_a_r1):04d}"])
                cmd_b_parts.extend([f"L0{clamp(center_l0):04d}", f"R2{clamp(pos_b_r2):04d}", f"R1{clamp(pos_b_r1):04d}"])

            elif self.motion_mode == "toe_tease":
                # Quick flickering pitch (R2) to tap the toes.
                # L0 remains relatively steady but close.
                # Use a 2x frequency multiplier for a faster "teasing" feel.
                fast_phase_a = phase_a * 2.0
                fast_phase_b = phase_b * 2.0

                # Toes point "down" to tap towards the center
                # Assuming R2 < 5000 is pointing toes down. We sweep between 5000 and (5000 - amp_r2)
                pos_a_r2 = center_rx - (amp_r2 / 2.0) - (amp_r2 / 2.0) * math.sin(fast_phase_a)
                pos_b_r2 = center_rx - (amp_r2 / 2.0) - (amp_r2 / 2.0) * math.sin(fast_phase_b)

                # Slight pulsing L0
                pos_l0 = center_l0 + (amp_l0 * 0.1) * math.sin(phase_a)

                cmd_a_parts.extend([f"L0{clamp(pos_l0):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_l0):04d}", f"R2{clamp(pos_b_r2):04d}"])

            elif self.motion_mode == "edge_stroking":
                # Feet roll heavily INWARDS (R1) to create a tight V-groove with the soles touching.
                # Left rolls in (+R1?), Right rolls in (-R1?). We'll hold it steady.
                pos_a_r1 = center_rx + amp_r1
                pos_b_r1 = center_rx - amp_r1

                # L0 synchronously strokes up and down the groove
                pos_l0 = center_l0 + amp_l0 * math.sin(phase_a)

                # Slight pitch to keep the stroke parallel to the target
                pos_r2 = center_rx + amp_r2 * math.sin(phase_a)

                cmd_a_parts.extend([f"L0{clamp(pos_l0):04d}", f"R1{clamp(pos_a_r1):04d}", f"R2{clamp(pos_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_l0):04d}", f"R1{clamp(pos_b_r1):04d}", f"R2{clamp(pos_r2):04d}"])

            elif self.motion_mode == "heel_press":
                # Toes pitched heavily UP (away from target) to expose the heels.
                # Assuming R2 > 5000 is pitch up.
                pos_r2 = center_rx + amp_r2

                # Deep, slow squeezing L0
                slow_phase = phase_a * 0.5
                pos_l0 = center_l0 + amp_l0 * math.sin(slow_phase)

                # Twisting (R0) slightly back and forth to grind the heels
                pos_a_r0 = center_rx + amp_r0 * math.cos(slow_phase)
                pos_b_r0 = center_rx - amp_r0 * math.cos(slow_phase)

                cmd_a_parts.extend([f"L0{clamp(pos_l0):04d}", f"R2{clamp(pos_r2):04d}", f"R0{clamp(pos_a_r0):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_l0):04d}", f"R2{clamp(pos_r2):04d}", f"R0{clamp(pos_b_r0):04d}"])

            elif self.motion_mode == "circling_tease":
                # Feet held gently on the target.
                # Roll (R1) and Pitch (R2) move in a circular sine/cosine pattern to create a grinding orbital motion.
                pos_a_r1 = center_rx + amp_r1 * math.sin(phase_a)
                pos_b_r1 = center_rx - amp_r1 * math.sin(phase_a) # mirror roll

                pos_a_r2 = center_rx + amp_r2 * math.cos(phase_a)
                pos_b_r2 = center_rx + amp_r2 * math.cos(phase_a) # sync pitch

                cmd_a_parts.extend([f"L0{clamp(center_l0):04d}", f"R1{clamp(pos_a_r1):04d}", f"R2{clamp(pos_a_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(center_l0):04d}", f"R1{clamp(pos_b_r1):04d}", f"R2{clamp(pos_b_r2):04d}"])

            else: # fallback
                pos_a = center_l0 + amp_l0 * math.sin(phase_a)
                pos_b = center_l0 + amp_l0 * math.sin(phase_b)
                cmd_a_parts.append(f"L0{clamp(pos_a):04d}")
                cmd_b_parts.append(f"L0{clamp(pos_b):04d}")"""

content = content.replace(old_loop, new_loop)

# Update phase shift logic for the new modes
old_update = """        # In some modes, we want synchronous base loops
        if mode in ["v_stroke", "wrapping_twist", "sole_rub"]:
            self.controller.phase_shift = 0   # Base phase sync (modes handle mirroring internally if needed)
        else:
            self.controller.phase_shift = 180 # Base phase alternating (e.g. alternating_step)"""

new_update = """        # In some modes, we want synchronous base loops
        if mode in ["v_stroke", "wrapping_twist", "sole_rub", "edge_stroking", "heel_press", "circling_tease", "toe_tease"]:
            self.controller.phase_shift = 0   # Base phase sync (modes handle mirroring internally if needed)
        else:
            self.controller.phase_shift = 180 # Base phase alternating (e.g. alternating_step)"""

content = content.replace(old_update, new_update)

with open('dual_osr_control.py', 'w') as f:
    f.write(content)
