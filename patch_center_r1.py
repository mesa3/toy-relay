import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    old = '''            # Centers (0-9999)
            center_l0 = (self.base_squeeze / 100.0) * 9999
            center_l2 = 5000
            center_rx = 5000
            center_r2 = (self.ankle_angle_offset / 100.0) * 9999'''

    new = '''            # Centers (0-9999)
            center_l0 = (self.base_squeeze / 100.0) * 9999
            center_l2 = 5000
            center_r1 = (self.roll_angle_offset / 100.0) * 9999
            center_rx = center_r1 # Backwards compatibility for unmodified modes
            center_r2 = (self.ankle_angle_offset / 100.0) * 9999'''

    if old in content:
        content = content.replace(old, new)
        with open('dual_osr_control.py', 'w') as f:
            f.write(content)
        print("Patched successfully")
    else:
        print("Could not find string")

patch()
