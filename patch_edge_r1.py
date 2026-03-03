import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # The issue is in edge_stroking
    old = '''            elif self.motion_mode == "edge_stroking":
                # Feet roll heavily INWARDS (R1) to create a tight V-groove with the soles touching.
                pos_a_r1 = center_r1 + amp_r1
                pos_b_r1 = center_r1 - amp_r1'''

    new = '''            elif self.motion_mode == "edge_stroking":
                # Feet roll heavily INWARDS (R1) to create a tight V-groove with the soles touching.
                pos_a_r1 = center_a_r1 + amp_r1
                pos_b_r1 = center_b_r1 - amp_r1'''

    if old in content:
        content = content.replace(old, new)
        with open('dual_osr_control.py', 'w') as f:
            f.write(content)
        print("Patched successfully")
    else:
        print("Could not find string")

patch()
