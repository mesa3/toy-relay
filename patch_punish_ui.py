import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # 1. Add to UI
    ui_old = '''            "wave_rub_up_down", "wave_rub_front_back", "static_rub_front_back", "asymmetric_sprint",'''
    ui_new = '''            "wave_rub_up_down", "wave_rub_front_back", "static_rub_front_back", "asymmetric_sprint",
            "foot_slap", "glans_torture",'''
    content = content.replace(ui_old, ui_new)

    # 2. Add to sync list (for glans_torture, foot_slap handles own phases but let's keep it safe)
    sync_old = '''                    "wave_rub_front_back", "static_rub_front_back", "asymmetric_sprint",'''
    sync_new = '''                    "wave_rub_front_back", "static_rub_front_back", "asymmetric_sprint", "foot_slap", "glans_torture",'''
    content = content.replace(sync_old, sync_new)

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
print("UI updated")
