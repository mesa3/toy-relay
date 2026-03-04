import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # Oh, I missed other modes where B uses center_r1. Let's globally replace `pos_b_r1 = center_r1` with `pos_b_r1 = center_b_r1`
    content = content.replace("pos_b_r1 = center_r1 -", "pos_b_r1 = center_b_r1 -")
    content = content.replace("pos_b_r1 = center_r1 +", "pos_b_r1 = center_b_r1 +")

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
print("All center_r1 patched")
