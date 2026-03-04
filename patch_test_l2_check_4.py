def patch():
    with open('tests/test_dual_osr_control.py', 'r') as f:
        content = f.read()

    lines = content.split('\n')
    out = []
    for line in lines:
        out.append(line)
        if "gui.ankle_angle_offset_var.get.return_value = 50.0" in line:
            out.append("            gui.reverse_l2_var = MagicMock()")
            out.append("            gui.reverse_l2_var.get.return_value = True")

    with open('tests/test_dual_osr_control.py', 'w') as f:
        f.write('\n'.join(out))

patch()
