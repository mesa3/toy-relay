with open('tests/test_dual_osr_control.py', 'r') as f:
    content = f.read()

content = content.replace('"walk"', '"v_stroke"')
content = content.replace('["walk", "squeeze_rub", "ankle_massage", "stepping", "twisting"]', '["v_stroke", "alternating_step", "wrapping_twist", "sole_rub"]')

with open('tests/test_dual_osr_control.py', 'w') as f:
    f.write(content)
