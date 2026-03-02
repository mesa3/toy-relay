with open('tests/test_dual_osr_control.py', 'r') as f:
    content = f.read()

content = content.replace('["v_stroke", "alternating_step", "wrapping_twist", "sole_rub", "toe_tease", "edge_stroking", "heel_press", "circling_tease"]', '["v_stroke", "alternating_step", "wrapping_twist", "sole_rub", "toe_tease", "edge_stroking", "heel_press", "circling_tease", "single_foot_tease_left", "single_foot_tease_right", "single_foot_stroke_left", "single_foot_stroke_right"]')

with open('tests/test_dual_osr_control.py', 'w') as f:
    f.write(content)
