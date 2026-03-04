import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # Rename L1 to L2 everywhere in the motion loop logic
    # Also we need to replace the definition of center_l1 and amp_l1 to l2

    # 1. Update variables
    content = content.replace("amp_l1 =", "amp_l2 =")
    content = content.replace("center_l1 = 5000", "center_l2 = 5000")

    # 2. Update all uses of L1 and pos_*_l1
    content = content.replace("pos_a_l1", "pos_a_l2")
    content = content.replace("pos_b_l1", "pos_b_l2")
    content = content.replace("L1{clamp(", "L2{clamp(")
    content = content.replace("center_l1", "center_l2")

    # The user said the devices are "hung on the wall" (vertical V-shape) and feet grip with the arch (horizontal).
    # When L0 extends (moving down and inward towards the penis), to keep it sliding strictly down the penis,
    # L2 (which typically moves the receiver UP/DOWN relative to the base) needs to compensate.
    # Assuming standard SR6: L0 extends -> moves payload away from base.
    # If the base is angled 45 deg down towards the center, extending L0 moves the foot closer to the center AND further down.
    # To keep the distance to the center constant (to just slide down), we must pull L2 UP (away from the center).
    # Since we want to stroke *along* the penis (which is vertical, same as the center axis), the primary motion is Z.
    # $L_0 = Z \times \cos(45^\circ)$
    # $L_2 = -Z \times \sin(45^\circ)$ (move opposite to the inward motion)
    # The math for the compensation is similar to before, just L2 instead of L1.

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
print("L1 changed to L2")
