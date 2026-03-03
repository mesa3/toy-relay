import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # 1. Remove UI
    ui_remove = '''        ttk.Label(ctrl_frame, text="L2 Lateral Gap / Squeeze (%):").pack(anchor="w", padx=5)
        self.l2_squeeze_var = tk.DoubleVar(value=50.0)
        self.l2_squeeze_scale = ttk.Scale(ctrl_frame, from_=0.0, to=100.0, variable=self.l2_squeeze_var, command=self.update_params)
        self.l2_squeeze_scale.pack(fill="x", padx=5, pady=2)

'''
    content = content.replace(ui_remove, '')

    # 2. Remove from init
    init_remove = '''        self.l2_squeeze = 50.0 # Base L2 gap offset\n'''
    content = content.replace(init_remove, '')

    # 3. Remove from update_params
    update_remove = '''        self.controller.l2_squeeze = self.l2_squeeze_var.get()\n'''
    content = content.replace(update_remove, '')

    # 4. Revert center calculation
    center_old = '''            center_l2 = (self.l2_squeeze / 100.0) * 9999'''
    center_new = '''            center_l2 = 5000'''
    content = content.replace(center_old, center_new)

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
print("Reverted L2 Squeeze")
