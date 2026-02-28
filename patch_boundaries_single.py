with open('test_boundaries.py', 'r') as f:
    content = f.read()

content = content.replace('["v_stroke", "alternating_step", "wrapping_twist", "sole_rub"]', '["v_stroke", "alternating_step", "wrapping_twist", "sole_rub", "single_foot_tease_left", "single_foot_tease_right", "single_foot_stroke_left", "single_foot_stroke_right"]')

with open('test_boundaries.py', 'w') as f:
    f.write(content)
