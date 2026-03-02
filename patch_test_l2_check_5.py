import re

def patch():
    with open('tests/test_dual_osr_control.py', 'r') as f:
        content = f.read()

    # The issue is the test file has "ankle_offset_var", not "ankle_angle_offset_var" as I thought.
    # Let's fix that too while we're at it since dual_osr_control expects ankle_offset_var.

    old = '''            gui.ankle_offset_var = MagicMock()
            gui.ankle_offset_var.get.return_value = 50.0

            gui.update_params()'''

    new = '''            gui.ankle_offset_var = MagicMock()
            gui.ankle_offset_var.get.return_value = 50.0
            gui.reverse_l2_var = MagicMock()
            gui.reverse_l2_var.get.return_value = True

            gui.update_params()'''

    content = content.replace(old, new)

    with open('tests/test_dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
