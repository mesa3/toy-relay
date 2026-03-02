with open('dual_osr_control.py', 'r') as f:
    content = f.read()

old_init = """        self.pitch_amp = 50.0  # R2
        self.roll_amp = 50.0   # R1
        self.twist_amp = 50.0  # R0
        self.base_squeeze = 50.0 # Base L0 offset
        self.motion_mode = "v_stroke"
"""

new_init = """        self.pitch_amp = 50.0  # R2
        self.roll_amp = 50.0   # R1
        self.twist_amp = 50.0  # R0
        self.base_squeeze = 50.0 # Base L0 offset
        self.ankle_angle_offset = 50.0 # Base R2 offset
        self.motion_mode = "v_stroke"
"""

content = content.replace(old_init, new_init)

with open('dual_osr_control.py', 'w') as f:
    f.write(content)
