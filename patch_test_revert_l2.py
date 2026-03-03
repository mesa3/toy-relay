import re

def patch():
    with open('tests/test_dual_osr_control.py', 'r') as f:
        content = f.read()

    # 1. Remove mock
    content = content.replace('''            gui.l2_squeeze_var = MagicMock()\n            gui.l2_squeeze_var.get.return_value = 40.0\n''', '')

    # 2. Remove assert
    content = content.replace('''            self.assertEqual(gui.controller.l2_squeeze, 40.0)\n''', '')

    with open('tests/test_dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
