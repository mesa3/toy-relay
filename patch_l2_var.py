def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # Find where twist scale is packed
    target = '''        self.twist_scale = ttk.Scale(adv_frame, from_=0.0, to=100.0, variable=self.twist_amp_var, command=self.update_params)
        self.twist_scale.pack(fill="x", padx=5, pady=2)'''

    replacement = '''        self.twist_scale = ttk.Scale(adv_frame, from_=0.0, to=100.0, variable=self.twist_amp_var, command=self.update_params)
        self.twist_scale.pack(fill="x", padx=5, pady=2)

        self.reverse_l2_var = tk.BooleanVar(value=False)
        self.reverse_l2_check = ttk.Checkbutton(adv_frame, text="Reverse L2 Compensation Direction", variable=self.reverse_l2_var, command=self.update_params)
        self.reverse_l2_check.pack(anchor="w", padx=5, pady=5)'''

    content = content.replace(target, replacement)

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
