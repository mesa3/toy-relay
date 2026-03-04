import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # Add to UI list
    ui_old = '''            "wave_rub_up_down", "wave_rub_front_back", "static_rub_front_back",'''
    ui_new = '''            "wave_rub_up_down", "wave_rub_front_back", "static_rub_front_back", "asymmetric_sprint",'''
    content = content.replace(ui_old, ui_new)

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
print("UI modified")
