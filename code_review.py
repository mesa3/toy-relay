# Simulating Code Review
import subprocess

def test_imports():
    try:
        import dual_osr_control
        print("Imports OK")
    except Exception as e:
        print(f"Error: {e}")

test_imports()
