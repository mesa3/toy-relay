import re

with open('dual_osr_control.py', 'r') as f:
    content = f.read()

# Add slider
old_slider = """        # Advanced Axes
        adv_frame = ttk.LabelFrame(ctrl_frame, text="Advanced Axes (Depends on Mode)")
        adv_frame.pack(fill="x", padx=5, pady=5)

        # Pitch (R2)"""

new_slider = """        # Advanced Axes
        adv_frame = ttk.LabelFrame(ctrl_frame, text="Advanced Axes (Depends on Mode)")
        adv_frame.pack(fill="x", padx=5, pady=5)

        # Ankle Pitch Offset (R2 Base)
        ttk.Label(adv_frame, text="Ankle Pitch Offset R2 Base (%):").pack(anchor="w", padx=5)
        self.ankle_offset_var = tk.DoubleVar(value=50.0)
        self.ankle_scale = ttk.Scale(adv_frame, from_=0.0, to=100.0, variable=self.ankle_offset_var, command=self.update_params)
        self.ankle_scale.pack(fill="x", padx=5, pady=2)

        # Pitch (R2)"""

content = content.replace(old_slider, new_slider)

# Update params
old_update = """        self.controller.base_squeeze = self.base_squeeze_var.get()
        self.controller.pitch_amp = self.pitch_amp_var.get()"""

new_update = """        self.controller.base_squeeze = self.base_squeeze_var.get()
        self.controller.ankle_angle_offset = self.ankle_offset_var.get()
        self.controller.pitch_amp = self.pitch_amp_var.get()"""

content = content.replace(old_update, new_update)

# Fix geometry size again to fit the new slider
content = content.replace('self.root.geometry("600x850")', 'self.root.geometry("600x900")')

with open('dual_osr_control.py', 'w') as f:
    f.write(content)
