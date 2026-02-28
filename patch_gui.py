import re

with open('dual_osr_control.py', 'r') as f:
    content = f.read()

gui_old = """        # Stroke
        ttk.Label(ctrl_frame, text="Stroke Length (%):").pack(anchor="w", padx=5)
        self.stroke_var = tk.DoubleVar(value=50.0)
        self.stroke_scale = ttk.Scale(ctrl_frame, from_=0.0, to=100.0, variable=self.stroke_var, command=self.update_params)
        self.stroke_scale.pack(fill="x", padx=5, pady=2)

        # Offset
        ttk.Label(ctrl_frame, text="Center Offset (%):").pack(anchor="w", padx=5)
        self.offset_var = tk.DoubleVar(value=50.0)
        self.offset_scale = ttk.Scale(ctrl_frame, from_=0.0, to=100.0, variable=self.offset_var, command=self.update_params)
        self.offset_scale.pack(fill="x", padx=5, pady=2)

        # Mode (Sync vs Alternating)
        mode_frame = ttk.Frame(ctrl_frame)
        mode_frame.pack(fill="x", padx=5, pady=10)
        self.mode_var = tk.StringVar(value="alternating")
        ttk.Radiobutton(mode_frame, text="Alternating (Walk)", variable=self.mode_var, value="alternating", command=self.update_params).pack(side="left", padx=10)
        ttk.Radiobutton(mode_frame, text="Sync (Jump)", variable=self.mode_var, value="sync", command=self.update_params).pack(side="left", padx=10)"""

gui_new = """        # Mode Selection
        mode_frame = ttk.Frame(ctrl_frame)
        mode_frame.pack(fill="x", padx=5, pady=5)
        ttk.Label(mode_frame, text="Motion Mode:").pack(side="left")
        self.mode_var = tk.StringVar(value="walk")
        modes = ["walk", "squeeze_rub", "ankle_massage", "stepping", "twisting"]
        self.mode_combo = ttk.Combobox(mode_frame, textvariable=self.mode_var, values=modes, state="readonly")
        self.mode_combo.pack(side="left", padx=5)
        self.mode_combo.bind("<<ComboboxSelected>>", self.update_params)

        # Stroke / Base Squeeze (L0)
        ttk.Label(ctrl_frame, text="L0 Stroke Length (%):").pack(anchor="w", padx=5)
        self.stroke_var = tk.DoubleVar(value=50.0)
        self.stroke_scale = ttk.Scale(ctrl_frame, from_=0.0, to=100.0, variable=self.stroke_var, command=self.update_params)
        self.stroke_scale.pack(fill="x", padx=5, pady=2)

        ttk.Label(ctrl_frame, text="L0 Base Squeeze Offset (%):").pack(anchor="w", padx=5)
        self.base_squeeze_var = tk.DoubleVar(value=50.0)
        self.base_squeeze_scale = ttk.Scale(ctrl_frame, from_=0.0, to=100.0, variable=self.base_squeeze_var, command=self.update_params)
        self.base_squeeze_scale.pack(fill="x", padx=5, pady=2)

        # Advanced Axes
        adv_frame = ttk.LabelFrame(ctrl_frame, text="Advanced Axes (Depends on Mode)")
        adv_frame.pack(fill="x", padx=5, pady=5)

        # Pitch (R2)
        ttk.Label(adv_frame, text="Pitch Amplitude R2 (%):").pack(anchor="w", padx=5)
        self.pitch_amp_var = tk.DoubleVar(value=50.0)
        self.pitch_scale = ttk.Scale(adv_frame, from_=0.0, to=100.0, variable=self.pitch_amp_var, command=self.update_params)
        self.pitch_scale.pack(fill="x", padx=5, pady=2)

        # Roll (R1)
        ttk.Label(adv_frame, text="Roll Amplitude R1 (%):").pack(anchor="w", padx=5)
        self.roll_amp_var = tk.DoubleVar(value=50.0)
        self.roll_scale = ttk.Scale(adv_frame, from_=0.0, to=100.0, variable=self.roll_amp_var, command=self.update_params)
        self.roll_scale.pack(fill="x", padx=5, pady=2)

        # Twist (R0)
        ttk.Label(adv_frame, text="Twist Amplitude R0 (%):").pack(anchor="w", padx=5)
        self.twist_amp_var = tk.DoubleVar(value=50.0)
        self.twist_scale = ttk.Scale(adv_frame, from_=0.0, to=100.0, variable=self.twist_amp_var, command=self.update_params)
        self.twist_scale.pack(fill="x", padx=5, pady=2)"""

content = content.replace(gui_old, gui_new)

update_params_old = """    def update_params(self, _=None):
        self.controller.speed = self.speed_var.get()
        self.controller.stroke = self.stroke_var.get()
        self.controller.offset = self.offset_var.get()
        if self.mode_var.get() == "sync":
            self.controller.phase_shift = 0
        else:
            self.controller.phase_shift = 180"""

update_params_new = """    def update_params(self, _=None):
        self.controller.speed = self.speed_var.get()
        self.controller.stroke = self.stroke_var.get()
        self.controller.base_squeeze = self.base_squeeze_var.get()
        self.controller.pitch_amp = self.pitch_amp_var.get()
        self.controller.roll_amp = self.roll_amp_var.get()
        self.controller.twist_amp = self.twist_amp_var.get()

        mode = self.mode_var.get()
        self.controller.motion_mode = mode

        # In twisting or squeeze mode, they often operate in sync or have specialized phase handling
        if mode == "squeeze_rub":
            self.controller.phase_shift = 0  # Sync L0
        else:
            self.controller.phase_shift = 180 # Alternating L0"""

content = content.replace(update_params_old, update_params_new)

# Increase the window size a little bit so everything fits
content = content.replace('self.root.geometry("600x700")', 'self.root.geometry("600x850")')

with open('dual_osr_control.py', 'w') as f:
    f.write(content)
