import re

def patch():
    with open('tests/test_dual_osr_control.py', 'r') as f:
        content = f.read()

    content = content.replace("gui.pitch_var =", "gui.pitch_amp_var =")
    content = content.replace("gui.pitch_var.get", "gui.pitch_amp_var.get")
    content = content.replace("gui.roll_var =", "gui.roll_amp_var =")
    content = content.replace("gui.roll_var.get", "gui.roll_amp_var.get")
    content = content.replace("gui.twist_var =", "gui.twist_amp_var =")
    content = content.replace("gui.twist_var.get", "gui.twist_amp_var.get")
    content = content.replace("gui.ankle_offset_var =", "gui.ankle_angle_offset_var =")
    content = content.replace("gui.ankle_offset_var.get", "gui.ankle_angle_offset_var.get")

    with open('tests/test_dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
