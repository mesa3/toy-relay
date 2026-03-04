import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # Define center_r0 explicitely as 5000 (neutral twist)
    old_centers = '''            center_r1 = (self.roll_angle_offset / 100.0) * 9999
            center_rx = center_r1 # Backwards compatibility for unmodified modes
            center_r2 = (self.ankle_angle_offset / 100.0) * 9999'''

    new_centers = '''            center_r1 = (self.roll_angle_offset / 100.0) * 9999
            center_r0 = 5000 # Neutral twist
            center_rx = center_r1 # Backwards compatibility for unmodified modes
            center_r2 = (self.ankle_angle_offset / 100.0) * 9999'''

    content = content.replace(old_centers, new_centers)

    # Now replace all instances of R0{clamp(pos_a_r0)} where the formula for pos_a_r0 uses center_rx
    content = content.replace("pos_a_r0 = center_rx", "pos_a_r0 = center_r0")
    content = content.replace("pos_b_r0 = center_rx", "pos_b_r0 = center_r0")

    # Replace center_rx directly in the R0 output formatted string if any
    content = content.replace("R0{clamp(center_rx):04d}", "R0{clamp(center_r0):04d}")

    # Now that R0 explicitly uses center_r0, center_rx is only acting as a proxy for center_r1.
    # We can replace all remaining uses of center_rx with center_r1 for clarity.
    content = content.replace("pos_a_r1 = center_rx", "pos_a_r1 = center_r1")
    content = content.replace("pos_b_r1 = center_rx", "pos_b_r1 = center_r1")
    content = content.replace("R1{clamp(center_rx):04d}", "R1{clamp(center_r1):04d}")

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
print("R0 decoupled from R1 base offset")
