import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # edge_stroking - uses L0 heavily, so we MUST add L1 compensation
    edge_old = '''            elif self.motion_mode == "edge_stroking":
                # Feet roll heavily INWARDS (R1) to create a tight V-groove with the soles touching.
                # Left rolls in (+R1?), Right rolls in (-R1?). We'll hold it steady.
                pos_a_r1 = center_rx + amp_r1
                pos_b_r1 = center_rx - amp_r1

                # L0 synchronously strokes up and down the groove
                pos_l0 = center_l0 + amp_l0 * math.sin(phase_a)

                # Slight pitch to keep the stroke parallel to the target
                pos_r2 = center_r2 + amp_r2 * math.sin(phase_a)

                cmd_a_parts.extend([f"L0{clamp(pos_l0):04d}", f"R1{clamp(pos_a_r1):04d}", f"R2{clamp(pos_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_l0):04d}", f"R1{clamp(pos_b_r1):04d}", f"R2{clamp(pos_r2):04d}"])'''

    edge_new = '''            elif self.motion_mode == "edge_stroking":
                # Feet roll heavily INWARDS (R1) to create a tight V-groove with the soles touching.
                pos_a_r1 = center_rx + amp_r1
                pos_b_r1 = center_rx - amp_r1

                # L0 synchronously strokes up and down the groove
                z_motion = amp_l0 * math.sin(phase_a)
                pos_l0 = center_l0 + z_motion

                # Compensate laterally
                pos_a_l1 = center_l1 - z_motion
                pos_b_l1 = center_l1 + z_motion

                # Fix pitch to stay parallel instead of bobbing up and down
                pos_r2 = center_r2

                cmd_a_parts.extend([f"L0{clamp(pos_l0):04d}", f"L1{clamp(pos_a_l1):04d}", f"R1{clamp(pos_a_r1):04d}", f"R2{clamp(pos_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_l0):04d}", f"L1{clamp(pos_b_l1):04d}", f"R1{clamp(pos_b_r1):04d}", f"R2{clamp(pos_r2):04d}"])'''
    content = content.replace(edge_old, edge_new)

    # heel_press - uses L0, add L1 compensation
    heel_old = '''            elif self.motion_mode == "heel_press":
                # Toes pitched heavily UP (away from target) to expose the heels.
                # Assuming R2 > 5000 is pitch up.
                pos_r2 = center_r2 + amp_r2

                # Deep, slow squeezing L0
                pos_l0 = center_l0 + amp_l0 * math.sin(phase_a)

                cmd_a_parts.extend([f"L0{clamp(pos_l0):04d}", f"R2{clamp(pos_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_l0):04d}", f"R2{clamp(pos_r2):04d}"])'''

    heel_new = '''            elif self.motion_mode == "heel_press":
                # Toes pitched heavily UP (away from target) to expose the heels.
                pos_r2 = center_r2 + amp_r2

                # Deep, slow squeezing L0
                z_motion = amp_l0 * math.sin(phase_a)
                pos_l0 = center_l0 + z_motion

                pos_a_l1 = center_l1 - z_motion
                pos_b_l1 = center_l1 + z_motion

                cmd_a_parts.extend([f"L0{clamp(pos_l0):04d}", f"L1{clamp(pos_a_l1):04d}", f"R2{clamp(pos_r2):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_l0):04d}", f"L1{clamp(pos_b_l1):04d}", f"R2{clamp(pos_r2):04d}"])'''
    content = content.replace(heel_old, heel_new)

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
print("More patched 2")
