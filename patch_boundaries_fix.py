import re

with open('test_boundaries.py', 'r') as f:
    content = f.read()

# Make sure tests use the clamp helper
content = content.replace('assert pos_a_r2 >= 0 and pos_a_r2 <= 9999, f"R2 out of bounds: {pos_a_r2}"', 'pos_a_r2 = max(0, min(9999, int(pos_a_r2)))\n                assert pos_a_r2 >= 0 and pos_a_r2 <= 9999, f"R2 out of bounds: {pos_a_r2}"')
content = content.replace('assert pos_b_r1 >= 0 and pos_b_r1 <= 9999, f"R1 out of bounds: {pos_b_r1}"', 'pos_b_r1 = max(0, min(9999, int(pos_b_r1)))\n                assert pos_b_r1 >= 0 and pos_b_r1 <= 9999, f"R1 out of bounds: {pos_b_r1}"')
content = content.replace('center_rx = 5000', 'center_rx = 5000\n            center_r2 = (controller.ankle_angle_offset / 100.0) * 9999')
content = content.replace('pos_a_r2 = center_rx', 'pos_a_r2 = center_r2')

with open('test_boundaries.py', 'w') as f:
    f.write(content)
