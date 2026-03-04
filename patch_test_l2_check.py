import re

def patch():
    with open('tests/test_dual_osr_control.py', 'r') as f:
        content = f.read()

    old_test = '''            gui.ankle_angle_offset_var = MagicMock()
            gui.ankle_angle_offset_var.get.return_value = 50.0

            gui.update_params()'''

    new_test = '''            gui.ankle_angle_offset_var = MagicMock()
            gui.ankle_angle_offset_var.get.return_value = 50.0
            gui.reverse_l2_var = MagicMock()
            gui.reverse_l2_var.get.return_value = True

            gui.update_params()'''

    content = content.replace(old_test, new_test)

    old_assert = '''            self.assertEqual(gui.controller.phase_shift, 180)'''
    new_assert = '''            self.assertEqual(gui.controller.phase_shift, 180)
            self.assertEqual(gui.controller.reverse_l2, True)'''
    content = content.replace(old_assert, new_assert)

    with open('tests/test_dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
