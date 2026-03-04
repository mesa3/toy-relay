import re

def test():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()
    if 'L2{' in content and 'L1{' not in content:
        print("PASS")
    else:
        print("FAIL")

test()
