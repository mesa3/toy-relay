import re

with open('test_boundaries.py', 'r') as f:
    content = f.read()

content = content.replace('controller.base_squeeze = 100.0', 'controller.base_squeeze = 100.0\n    controller.ankle_angle_offset = 100.0')

with open('test_boundaries.py', 'w') as f:
    f.write(content)
