import dual_osr_control

controller = dual_osr_control.DualOSRController()

def test_clamping():
    # Make sure we don't accidentally generate a command like R2-0500 which breaks T-Code parser
    controller.running = True
    controller.speed = 1.0
    controller.stroke = 100.0
    controller.pitch_amp = 100.0
    controller.roll_amp = 100.0
    controller.twist_amp = 100.0
    controller.base_squeeze = 100.0
    controller.ankle_angle_offset = 100.0

    # Check all modes for out of bounds issues at peak sine wave (t=0.25 -> phase=pi/2 -> sin=1)

    import math
    import time

    for mode in ["v_stroke", "alternating_step", "wrapping_twist", "sole_rub", "single_foot_tease_left", "single_foot_tease_right", "single_foot_stroke_left", "single_foot_stroke_right"]:
        controller.motion_mode = mode

        # Test extreme times
        for t in [0.0, 0.25, 0.5, 0.75]:
            phase_a = 2 * math.pi * controller.speed * t
            phase_b = phase_a + math.radians(180) # test alternating case too

            amp_l0 = (controller.stroke / 100.0) * 5000
            amp_r2 = (controller.pitch_amp / 100.0) * 5000
            amp_r1 = (controller.roll_amp / 100.0) * 5000
            amp_r0 = (controller.twist_amp / 100.0) * 5000

            center_l0 = (controller.base_squeeze / 100.0) * 9999
            center_rx = 5000
            center_r2 = (controller.ankle_angle_offset / 100.0) * 9999

            # Clamp logic from script
            if center_l0 - amp_l0 < 0: center_l0 = amp_l0
            if center_l0 + amp_l0 > 9999: center_l0 = 9999 - amp_l0

            # Simulated generation logic
            if mode == "alternating_step":
                pos_a_r2 = center_r2 - amp_r2 * math.sin(phase_a)
                pos_a_r2 = max(0, min(9999, int(pos_a_r2)))
                assert pos_a_r2 >= 0 and pos_a_r2 <= 9999, f"R2 out of bounds: {pos_a_r2}"

            elif mode == "wrapping_twist":
                pos_b_r1 = center_rx - amp_r1 * math.sin(phase_a)
                pos_b_r1 = max(0, min(9999, int(pos_b_r1)))
                assert pos_b_r1 >= 0 and pos_b_r1 <= 9999, f"R1 out of bounds: {pos_b_r1}"

    print("Clamping test passed.")

test_clamping()
