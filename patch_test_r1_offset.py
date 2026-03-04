import re

def patch():
    with open('tests/test_dual_osr_control.py', 'r') as f:
        content = f.read()

    old = '''            gui.ankle_offset_var = MagicMock()
            gui.ankle_offset_var.get.return_value = 50.0
            gui.reverse_l2_var = MagicMock()
            gui.reverse_l2_var.get.return_value = True

            gui.update_params()'''

    new = '''            gui.ankle_offset_var = MagicMock()
            gui.ankle_offset_var.get.return_value = 50.0
            gui.roll_offset_var = MagicMock()
            gui.roll_offset_var.get.return_value = 50.0
            gui.reverse_l2_var = MagicMock()
            gui.reverse_l2_var.get.return_value = True

            gui.update_params()'''

    content = content.replace(old, new)

    old_assert = '''            self.assertEqual(gui.controller.ankle_angle_offset, 50.0)'''
    new_assert = '''            self.assertEqual(gui.controller.ankle_angle_offset, 50.0)
            self.assertEqual(gui.controller.roll_angle_offset, 50.0)'''
    content = content.replace(old_assert, new_assert)

    with open('tests/test_dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
