import re

def patch():
    with open('tests/test_dual_osr_control.py', 'r') as f:
        content = f.read()

    # The offset logic was removed or replaced by base_squeeze in the actual app, but the test still checks for offset.
    # The actual update_params doesn't even set self.controller.offset anymore.
    # We should just assert the new variables.

    old_test = '''            self.assertEqual(gui.controller.speed, 2.0)
            self.assertEqual(gui.controller.stroke, 75.0)
            self.assertEqual(gui.controller.offset, 25.0)
            self.assertEqual(gui.controller.phase_shift, 180) # sync is not in the list that sets phase_shift to 0'''

    new_test = '''            self.assertEqual(gui.controller.speed, 2.0)
            self.assertEqual(gui.controller.stroke, 75.0)
            self.assertEqual(gui.controller.base_squeeze, 50.0)
            self.assertEqual(gui.controller.ankle_angle_offset, 50.0)
            self.assertEqual(gui.controller.pitch_amp, 50.0)
            self.assertEqual(gui.controller.roll_amp, 50.0)
            self.assertEqual(gui.controller.twist_amp, 50.0)
            self.assertEqual(gui.controller.phase_shift, 180)'''

    content = content.replace(old_test, new_test)

    with open('tests/test_dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
