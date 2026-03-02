import re

def patch():
    with open('tests/test_dual_osr_control.py', 'r') as f:
        content = f.read()

    old = '''            gui.ankle_angle_offset_var = MagicMock()
            gui.ankle_angle_offset_var.get.return_value = 50.0

            gui.update_params()'''

    # Turns out I had already successfully patched the assert, but missed the var initialization in the script. Let's just do a regex replace.
    content = re.sub(r'gui\.ankle_angle_offset_var\.get\.return_value = 50\.0\s+gui\.update_params\(\)',
                    '''gui.ankle_angle_offset_var.get.return_value = 50.0
            gui.reverse_l2_var = MagicMock()
            gui.reverse_l2_var.get.return_value = True

            gui.update_params()''', content)

    with open('tests/test_dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
