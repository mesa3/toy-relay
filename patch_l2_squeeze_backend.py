import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # 1. Init
    init_old = '''        self.base_squeeze = 50.0 # Base L0 offset
        self.ankle_angle_offset = 50.0 # Base R2 offset'''
    init_new = '''        self.base_squeeze = 50.0 # Base L0 offset
        self.l2_squeeze = 50.0 # Base L2 gap offset
        self.ankle_angle_offset = 50.0 # Base R2 offset'''
    content = content.replace(init_old, init_new)

    # 2. Update params
    update_old = '''        self.controller.base_squeeze = self.base_squeeze_var.get()
        self.controller.ankle_angle_offset = self.ankle_offset_var.get()'''
    update_new = '''        self.controller.base_squeeze = self.base_squeeze_var.get()
        self.controller.l2_squeeze = self.l2_squeeze_var.get()
        self.controller.ankle_angle_offset = self.ankle_offset_var.get()'''
    content = content.replace(update_old, update_new)

    # 3. Center calculation in motion_loop
    center_old = '''            # Centers (0-9999)
            center_l0 = (self.base_squeeze / 100.0) * 9999
            center_l2 = 5000
            center_r1 = (self.roll_angle_offset / 100.0) * 9999'''
    center_new = '''            # Centers (0-9999)
            center_l0 = (self.base_squeeze / 100.0) * 9999
            center_l2 = (self.l2_squeeze / 100.0) * 9999
            center_r1 = (self.roll_angle_offset / 100.0) * 9999'''
    content = content.replace(center_old, center_new)

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
print("Backend modified")
