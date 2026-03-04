import re

def patch():
    with open('tests/test_dual_osr_control.py', 'r') as f:
        content = f.read()

    # Need to add gui.reverse_l2_var since it's checked by update_params, but when the test runs update_params it throws.
    old = '''gui.ankle_angle_offset_var.get.return_value = 50.0'''
    new = '''gui.ankle_angle_offset_var.get.return_value = 50.0
            gui.reverse_l2_var = MagicMock()
            gui.reverse_l2_var.get.return_value = True'''

    # Turns out I did it but the replace was missed or skipped. Let's do it firmly.
    content = content.replace(
'''            gui.ankle_angle_offset_var = MagicMock()
            gui.ankle_angle_offset_var.get.return_value = 50.0

            gui.update_params()''',
'''            gui.ankle_angle_offset_var = MagicMock()
            gui.ankle_angle_offset_var.get.return_value = 50.0
            gui.reverse_l2_var = MagicMock()
            gui.reverse_l2_var.get.return_value = True

            gui.update_params()''')

    with open('tests/test_dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
