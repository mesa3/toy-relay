import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    ui_old = '''        ttk.Label(ctrl_frame, text="L0 Base Squeeze Offset (%):").pack(anchor="w", padx=5)
        self.base_squeeze_var = tk.DoubleVar(value=50.0)
        self.base_squeeze_scale = ttk.Scale(ctrl_frame, from_=0.0, to=100.0, variable=self.base_squeeze_var, command=self.update_params)
        self.base_squeeze_scale.pack(fill="x", padx=5, pady=2)

        # Advanced Axes'''

    ui_new = '''        ttk.Label(ctrl_frame, text="L0 Base Squeeze Offset (%):").pack(anchor="w", padx=5)
        self.base_squeeze_var = tk.DoubleVar(value=50.0)
        self.base_squeeze_scale = ttk.Scale(ctrl_frame, from_=0.0, to=100.0, variable=self.base_squeeze_var, command=self.update_params)
        self.base_squeeze_scale.pack(fill="x", padx=5, pady=2)

        ttk.Label(ctrl_frame, text="L2 Lateral Gap / Squeeze (%):").pack(anchor="w", padx=5)
        self.l2_squeeze_var = tk.DoubleVar(value=50.0)
        self.l2_squeeze_scale = ttk.Scale(ctrl_frame, from_=0.0, to=100.0, variable=self.l2_squeeze_var, command=self.update_params)
        self.l2_squeeze_scale.pack(fill="x", padx=5, pady=2)

        # Advanced Axes'''
    content = content.replace(ui_old, ui_new)

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
print("UI modified")
