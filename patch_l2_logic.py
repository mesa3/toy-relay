import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # The logic replaces pos_a_l2 = center_l2 - z_motion with an inverted calculation.
    # The simplest way is to introduce a compensation multiplier (+1 or -1) before adding to center.

    loop_old = '''            # Clamp L0
            if center_l0 - amp_l0 < 0: center_l0 = amp_l0
            if center_l0 + amp_l0 > 9999: center_l0 = 9999 - amp_l0'''

    loop_new = '''            # Clamp L0
            if center_l0 - amp_l0 < 0: center_l0 = amp_l0
            if center_l0 + amp_l0 > 9999: center_l0 = 9999 - amp_l0

            # L2 Compensation direction multiplier (based on wall mount orientation)
            l2_mult = -1.0 if self.reverse_l2 else 1.0'''
    content = content.replace(loop_old, loop_new)

    # v_stroke
    content = content.replace(
        '''pos_a_l2 = center_l2 - z_motion
                pos_b_l2 = center_l2 + z_motion''',
        '''pos_a_l2 = center_l2 - (z_motion * l2_mult)
                pos_b_l2 = center_l2 + (z_motion * l2_mult)'''
    )

    # alternating_step
    content = content.replace(
        '''pos_a_l2 = center_l2 - z_motion_a
                pos_b_l2 = center_l2 + z_motion_b''',
        '''pos_a_l2 = center_l2 - (z_motion_a * l2_mult)
                pos_b_l2 = center_l2 + (z_motion_b * l2_mult)'''
    )

    # toe tease
    content = content.replace(
        '''pos_a_l2 = center_l2 - z_motion_a
                pos_b_l2 = center_l2 + z_motion_b''',
        '''pos_a_l2 = center_l2 - (z_motion_a * l2_mult)
                pos_b_l2 = center_l2 + (z_motion_b * l2_mult)'''
    )

    # edge_stroking
    content = content.replace(
        '''pos_a_l2 = center_l2 - z_motion
                pos_b_l2 = center_l2 + z_motion''',
        '''pos_a_l2 = center_l2 - (z_motion * l2_mult)
                pos_b_l2 = center_l2 + (z_motion * l2_mult)'''
    )

    # heel_press
    content = content.replace(
        '''pos_a_l2 = center_l2 - z_motion
                pos_b_l2 = center_l2 + z_motion''',
        '''pos_a_l2 = center_l2 - (z_motion * l2_mult)
                pos_b_l2 = center_l2 + (z_motion * l2_mult)'''
    )

    # single_foot_tease_left
    content = content.replace(
        '''pos_a_l2 = center_l2 - z_motion_a''',
        '''pos_a_l2 = center_l2 - (z_motion_a * l2_mult)'''
    )

    # single_foot_tease_right
    content = content.replace(
        '''pos_b_l2 = center_l2 + z_motion_b''',
        '''pos_b_l2 = center_l2 + (z_motion_b * l2_mult)'''
    )

    # single_foot_stroke_left
    content = content.replace(
        '''pos_a_l2 = center_l2 - z_motion_a''',
        '''pos_a_l2 = center_l2 - (z_motion_a * l2_mult)'''
    )

    # single_foot_stroke_right
    content = content.replace(
        '''pos_b_l2 = center_l2 + z_motion_b''',
        '''pos_b_l2 = center_l2 + (z_motion_b * l2_mult)'''
    )

    with open('dual_osr_control.py', 'w') as f:
        f.write(content)

patch()
print("L2 Logic added")
