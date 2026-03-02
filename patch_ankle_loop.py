import re

with open('dual_osr_control.py', 'r') as f:
    content = f.read()

# Replace center_rx for R2
old_centers = """            # Centers (0-9999)
            center_l0 = (self.base_squeeze / 100.0) * 9999
            center_rx = 5000"""

new_centers = """            # Centers (0-9999)
            center_l0 = (self.base_squeeze / 100.0) * 9999
            center_rx = 5000
            center_r2 = (self.ankle_angle_offset / 100.0) * 9999"""

content = content.replace(old_centers, new_centers)

# Update all R2 references to use center_r2
content = re.sub(r'pos_a_r2 = center_rx', r'pos_a_r2 = center_r2', content)
content = re.sub(r'pos_b_r2 = center_rx', r'pos_b_r2 = center_r2', content)
content = re.sub(r'pos_r2 = center_rx', r'pos_r2 = center_r2', content)

with open('dual_osr_control.py', 'w') as f:
    f.write(content)
