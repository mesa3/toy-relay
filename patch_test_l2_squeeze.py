import re

def patch():
    with open('tests/test_dual_osr_control.py', 'r') as f:
        content = f.read()

    # 1. Add mock
    mock_old = '''            gui.base_squeeze_var = MagicMock()
            gui.base_squeeze_var.get.return_value = 50.0
            gui.ankle_offset_var = MagicMock()'''
    mock_new = '''            gui.base_squeeze_var = MagicMock()
            gui.base_squeeze_var.get.return_value = 50.0
            gui.l2_squeeze_var = MagicMock()
            gui.l2_squeeze_var.get.return_value = 40.0
            gui.ankle_offset_var = MagicMock()'''
    content = content.replace(mock_old, mock_new)

    # 2. Add assert
    assert_old = '''            self.assertEqual(gui.controller.base_squeeze, 50.0)
            self.assertEqual(gui.controller.ankle_angle_offset, 50.0)'''
    assert_new = '''            self.assertEqual(gui.controller.base_squeeze, 50.0)
            self.assertEqual(gui.controller.l2_squeeze, 40.0)
            self.assertEqual(gui.controller.ankle_angle_offset, 50.0)'''
    content = content.replace(assert_old, assert_new)

    with open('tests/test_dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
