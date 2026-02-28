import re

with open('dual_osr_control.py', 'r') as f:
    content = f.read()

old_gui = """        self.mode_var = tk.StringVar(value="v_stroke")
        modes = [
            "v_stroke", "alternating_step", "wrapping_twist", "sole_rub",
            "toe_tease", "edge_stroking", "heel_press", "circling_tease"
        ]"""

new_gui = """        self.mode_var = tk.StringVar(value="v_stroke")
        modes = [
            "v_stroke", "alternating_step", "wrapping_twist", "sole_rub",
            "toe_tease", "edge_stroking", "heel_press", "circling_tease",
            "single_foot_tease_left", "single_foot_tease_right",
            "single_foot_stroke_left", "single_foot_stroke_right"
        ]"""

content = content.replace(old_gui, new_gui)

with open('dual_osr_control.py', 'w') as f:
    f.write(content)
