import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    # Find the old foot_slap block
    old_block_start = '            elif self.motion_mode == "foot_slap":'
    old_block_end = '            elif self.motion_mode == "glans_torture":'

    # Use regex or string slicing to replace the block
    import re
    # We will use regex DOTALL to match across lines
    pattern = re.compile(r'            elif self\.motion_mode == "foot_slap":.*?            elif self\.motion_mode == "glans_torture":', re.DOTALL)

    new_block = '''            elif self.motion_mode == "foot_slap":
                # Redesigned Foot Slap (侧面脚耳光)
                # Goal: Side-slapping motion. Feet pull back laterally (L2) away from the penis,
                # then suddenly snap inward to strike the side, and bounce back.

                # Keep L0 static at the base squeeze position (or slightly pulled back to avoid tip)
                pos_l0 = center_l0

                # We need a custom slap profile based on the current phase progress (0 to 1)
                # Let's slow down the overall cycle so the "wait" is longer.
                slow_phase = phase_a * 0.5
                prog = (slow_phase % (2 * math.pi)) / (2 * math.pi)

                # We want Device A to slap at prog=0.25, and Device B to slap at prog=0.75
                # A slap profile goes from 1.0 (fully open/pulled back) down to -1.0 (fully closed/striking)
                def get_slap_val(t, strike_time):
                    # Distance from strike time
                    dist = abs(t - strike_time)
                    # If within 5% of cycle time, do the slap (very fast)
                    if dist < 0.05:
                        # Map dist 0->0.05 to -1.0->1.0
                        return -1.0 + (dist / 0.05) * 2.0
                    else:
                        # Recovering or waiting (fully open)
                        return 1.0

                val_a = get_slap_val(prog, 0.25)
                val_b = get_slap_val(prog, 0.75)

                # Map to L2.
                # Remember l2_mult handles mounting direction.
                # When val_a is 1.0 (open), we want L2 to move AWAY from center.
                # When val_a is -1.0 (slap), we want L2 to move TOWARDS center.
                # Previously: center_l2 - (z_motion * l2_mult). So if z_motion is positive, it moves inward.
                # We will map our val directly to a lateral motion offset.
                # amp_l0 represents the max stroke. We use it as the slap distance amplitude.
                lat_amp = amp_l0 * 0.8 # Slap distance

                # val is 1.0 (open) -> we want to subtract lat_amp (move outward)
                # val is -1.0 (slap) -> we want to add lat_amp (move inward to strike)
                # So offset = -val * lat_amp

                pos_a_l2 = center_l2 - (val_a * lat_amp * l2_mult)
                pos_b_l2 = center_l2 + (val_b * lat_amp * l2_mult)

                # Accompanied by a quick inward Roll (R1) flick to emphasize the "slapping with the sole"
                # R1 offset is 0 when open (val=1), and high amplitude when slapping (val=-1)
                r1_flick_a = ((1.0 - val_a) / 2.0) * amp_r1 # 0 to amp_r1
                r1_flick_b = ((1.0 - val_b) / 2.0) * amp_r1

                # pos_a_r1 = center_a_r1 + r1_flick_a (assuming + is inward roll)
                pos_a_r1 = center_a_r1 + r1_flick_a
                pos_b_r1 = center_b_r1 - r1_flick_b # mirrored

                # R2 stays neutral
                pos_a_r2 = center_r2
                pos_b_r2 = center_r2

                cmd_a_parts.extend([f"L0{clamp(pos_l0):04d}", f"L2{clamp(pos_a_l2):04d}", f"R2{clamp(pos_a_r2):04d}", f"R1{clamp(pos_a_r1):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_l0):04d}", f"L2{clamp(pos_b_l2):04d}", f"R2{clamp(pos_b_r2):04d}", f"R1{clamp(pos_b_r1):04d}"])

            elif self.motion_mode == "glans_torture":'''

    if pattern.search(content):
        content = pattern.sub(new_block, content)
        with open('dual_osr_control.py', 'w') as f:
            f.write(content)
        print("Foot slap redesigned successfully.")
    else:
        print("Regex failed to find target block.")

patch()
