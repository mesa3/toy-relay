with open('tests/test_dual_osr_control.py', 'r') as f:
    content = f.read()

content = content.replace('["v_stroke", "alternating_step", "wrapping_twist", "sole_rub"]', '["v_stroke", "alternating_step", "wrapping_twist", "sole_rub", "toe_tease", "edge_stroking", "heel_press", "circling_tease"]')

with open('tests/test_dual_osr_control.py', 'w') as f:
    f.write(content)
