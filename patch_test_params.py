import re

def patch():
    with open('tests/test_dual_osr_control.py', 'r') as f:
        content = f.read()

    old_test = '''            gui.speed_var = MagicMock()
            gui.speed_var.get.return_value = 2.0
            gui.stroke_var = MagicMock()
            gui.stroke_var.get.return_value = 75.0
            gui.offset_var = MagicMock()
            gui.offset_var.get.return_value = 25.0
            gui.mode_var = MagicMock()
            gui.mode_var.get.return_value = "sync"

            gui.update_params()

            self.assertEqual(gui.controller.speed, 2.0)
            self.assertEqual(gui.controller.stroke, 75.0)
            self.assertEqual(gui.controller.offset, 25.0)
            self.assertEqual(gui.controller.phase_shift, 0)'''

    new_test = '''            gui.speed_var = MagicMock()
            gui.speed_var.get.return_value = 2.0
            gui.stroke_var = MagicMock()
            gui.stroke_var.get.return_value = 75.0
            gui.offset_var = MagicMock()
            gui.offset_var.get.return_value = 25.0
            gui.mode_var = MagicMock()
            gui.mode_var.get.return_value = "sync"
            gui.pitch_var = MagicMock()
            gui.pitch_var.get.return_value = 50.0
            gui.roll_var = MagicMock()
            gui.roll_var.get.return_value = 50.0
            gui.twist_var = MagicMock()
            gui.twist_var.get.return_value = 50.0
            gui.base_squeeze_var = MagicMock()
            gui.base_squeeze_var.get.return_value = 50.0
            gui.ankle_offset_var = MagicMock()
            gui.ankle_offset_var.get.return_value = 50.0

            gui.update_params()

            self.assertEqual(gui.controller.speed, 2.0)
            self.assertEqual(gui.controller.stroke, 75.0)
            self.assertEqual(gui.controller.offset, 25.0)
            self.assertEqual(gui.controller.phase_shift, 180) # sync is not in the list that sets phase_shift to 0'''
    content = content.replace(old_test, new_test)

    with open('tests/test_dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
