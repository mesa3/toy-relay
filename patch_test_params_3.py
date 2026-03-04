import re

def patch():
    with open('tests/test_dual_osr_control.py', 'r') as f:
        content = f.read()

    content = content.replace("gui.ankle_angle_offset_var =", "gui.ankle_offset_var =")
    content = content.replace("gui.ankle_angle_offset_var.get", "gui.ankle_offset_var.get")

    with open('tests/test_dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
