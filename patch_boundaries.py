import re

with open('dual_osr_control.py', 'r') as f:
    content = f.read()

# Add a clamping helper to motion_loop
clamp_old = """            # Centers (0-9999)
            center_l0 = (self.base_squeeze / 100.0) * 9999
            center_rx = 5000

            # Clamp L0
            if center_l0 - amp_l0 < 0: center_l0 = amp_l0
            if center_l0 + amp_l0 > 9999: center_l0 = 9999 - amp_l0

            cmd_a_parts = []
            cmd_b_parts = []"""

clamp_new = """            # Centers (0-9999)
            center_l0 = (self.base_squeeze / 100.0) * 9999
            center_rx = 5000

            # Clamp L0
            if center_l0 - amp_l0 < 0: center_l0 = amp_l0
            if center_l0 + amp_l0 > 9999: center_l0 = 9999 - amp_l0

            def clamp(val):
                return max(0, min(9999, int(val)))

            cmd_a_parts = []
            cmd_b_parts = []"""

content = content.replace(clamp_old, clamp_new)

# Apply clamp to all f-strings
content = re.sub(r'int\((pos_[a-z0-9_]+|center_l0)\):04d', r'clamp(\1):04d', content)

with open('dual_osr_control.py', 'w') as f:
    f.write(content)
