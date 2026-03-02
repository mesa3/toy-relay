import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # 1. Add variable to DualOSRController init
    init_old = '''        self.ankle_angle_offset = 50.0 # Base R2 offset
        self.motion_mode = "v_stroke"'''
    init_new = '''        self.ankle_angle_offset = 50.0 # Base R2 offset
        self.motion_mode = "v_stroke"
        self.reverse_l2 = False # Reverse L2 compensation direction'''
    content = content.replace(init_old, init_new)

    # 2. Add checkbox to UI (under Advanced Axes frame)
    ui_old = '''        ttk.Label(adv_frame, text="Twist (R0) Amp (%):").pack(anchor="w", padx=5)
        self.twist_amp_var = tk.DoubleVar(value=50.0)
        self.twist_amp_scale = ttk.Scale(adv_frame, from_=0.0, to=100.0, variable=self.twist_amp_var, command=self.update_params)
        self.twist_amp_scale.pack(fill="x", padx=5, pady=2)'''
    ui_new = '''        ttk.Label(adv_frame, text="Twist (R0) Amp (%):").pack(anchor="w", padx=5)
        self.twist_amp_var = tk.DoubleVar(value=50.0)
        self.twist_amp_scale = ttk.Scale(adv_frame, from_=0.0, to=100.0, variable=self.twist_amp_var, command=self.update_params)
        self.twist_amp_scale.pack(fill="x", padx=5, pady=2)

        self.reverse_l2_var = tk.BooleanVar(value=False)
        self.reverse_l2_check = ttk.Checkbutton(adv_frame, text="Reverse L2 Compensation Direction", variable=self.reverse_l2_var, command=self.update_params)
        self.reverse_l2_check.pack(anchor="w", padx=5, pady=5)'''
    content = content.replace(ui_old, ui_new)

    # 3. Update update_params to read the checkbox
    update_old = '''        self.controller.pitch_amp = self.pitch_amp_var.get()
        self.controller.roll_amp = self.roll_amp_var.get()
        self.controller.twist_amp = self.twist_amp_var.get()'''
    update_new = '''        self.controller.pitch_amp = self.pitch_amp_var.get()
        self.controller.roll_amp = self.roll_amp_var.get()
        self.controller.twist_amp = self.twist_amp_var.get()
        self.controller.reverse_l2 = self.reverse_l2_var.get()'''
    content = content.replace(update_old, update_new)

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
print("L2 Checkbox added to UI")
