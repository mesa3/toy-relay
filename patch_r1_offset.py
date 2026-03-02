import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # 1. Add variable to DualOSRController init
    init_old = '''        self.base_squeeze = 50.0 # Base L0 offset
        self.ankle_angle_offset = 50.0 # Base R2 offset
        self.motion_mode = "v_stroke"'''
    init_new = '''        self.base_squeeze = 50.0 # Base L0 offset
        self.ankle_angle_offset = 50.0 # Base R2 offset
        self.roll_angle_offset = 50.0 # Base R1 offset
        self.motion_mode = "v_stroke"'''
    content = content.replace(init_old, init_new)

    # 2. Add slider to UI
    ui_old = '''        # Ankle Pitch Offset (R2 Base)
        ttk.Label(adv_frame, text="Ankle Pitch Offset R2 Base (%):").pack(anchor="w", padx=5)
        self.ankle_offset_var = tk.DoubleVar(value=50.0)
        self.ankle_scale = ttk.Scale(adv_frame, from_=0.0, to=100.0, variable=self.ankle_offset_var, command=self.update_params)
        self.ankle_scale.pack(fill="x", padx=5, pady=2)

        # Pitch (R2)
        ttk.Label(adv_frame, text="Pitch Amplitude R2 (%):").pack(anchor="w", padx=5)'''
    ui_new = '''        # Ankle Pitch Offset (R2 Base)
        ttk.Label(adv_frame, text="Ankle Pitch Offset R2 Base (%):").pack(anchor="w", padx=5)
        self.ankle_offset_var = tk.DoubleVar(value=50.0)
        self.ankle_scale = ttk.Scale(adv_frame, from_=0.0, to=100.0, variable=self.ankle_offset_var, command=self.update_params)
        self.ankle_scale.pack(fill="x", padx=5, pady=2)

        # Ankle Roll Offset (R1 Base)
        ttk.Label(adv_frame, text="Ankle Roll Offset R1 Base (%):").pack(anchor="w", padx=5)
        self.roll_offset_var = tk.DoubleVar(value=50.0)
        self.roll_offset_scale = ttk.Scale(adv_frame, from_=0.0, to=100.0, variable=self.roll_offset_var, command=self.update_params)
        self.roll_offset_scale.pack(fill="x", padx=5, pady=2)

        # Pitch (R2)
        ttk.Label(adv_frame, text="Pitch Amplitude R2 (%):").pack(anchor="w", padx=5)'''
    content = content.replace(ui_old, ui_new)

    # 3. Update update_params
    update_old = '''        self.controller.ankle_angle_offset = self.ankle_offset_var.get()
        self.controller.pitch_amp = self.pitch_amp_var.get()'''
    update_new = '''        self.controller.ankle_angle_offset = self.ankle_offset_var.get()
        self.controller.roll_angle_offset = self.roll_offset_var.get()
        self.controller.pitch_amp = self.pitch_amp_var.get()'''
    content = content.replace(update_old, update_new)

    # 4. Replace center_rx with center_r1 in motion loop
    loop_old = '''            # Centers (0-9999)
            center_l0 = (self.base_squeeze / 100.0) * 9999
            center_rx = 5000
            center_r2 = (self.ankle_angle_offset / 100.0) * 9999'''
    loop_new = '''            # Centers (0-9999)
            center_l0 = (self.base_squeeze / 100.0) * 9999
            center_r1 = (self.roll_angle_offset / 100.0) * 9999
            center_rx = center_r1 # Deprecated, keeping temporarily to avoid breaking other unpatched modes
            center_r2 = (self.ankle_angle_offset / 100.0) * 9999'''
    content = content.replace(loop_old, loop_new)

    # And specifically replace center_rx with center_r1 for the modes we patched.
    content = content.replace("R1{clamp(center_rx):04d}", "R1{clamp(center_r1):04d}")

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
print("R1 offset logic patched")
