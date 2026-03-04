import re

def patch():
    with open('dual_osr_control.py', 'r') as f:
        content = f.read()

    old_block_pattern = re.compile(r'            elif self\.motion_mode == "foot_slap":.*?            elif self\.motion_mode == "glans_torture":', re.DOTALL)

    new_block = '''            elif self.motion_mode == "foot_slap":
                # Foot Slap V3 (严谨节奏的单脚轮流大力扇耳光)
                # 节奏: A蓄力 -> A扇! -> A退回 -> B蓄力 -> B扇! -> B退回
                # 在一方动作时，另一方完全停在远处（Parked），绝不干涉。

                # director 进度 0.0 到 1.0 (控制完整的左右脚一轮)
                # 减慢一点整体进度，给舵机留出“大力挥动”的物理时间
                director = ( (phase_a * 0.4) % (2 * math.pi) ) / (2 * math.pi)

                # 定义几个关键位置
                park_l0 = center_l0 - amp_l0 * 0.5   # 停靠时稍微后退
                park_l2_offset = amp_l0 * 0.8        # 停靠时向外侧躲开

                windup_l0 = center_l0 - amp_l0       # 蓄力时退到最远
                windup_l2_offset = amp_l0            # 蓄力时张到最大
                windup_r2 = center_r2 + amp_r2       # 蓄力时脚腕上翻

                slap_l0 = center_l0 + amp_l0 * 0.5   # 扇下去时往前怼
                slap_l2_offset = 0                   # 扇下去时直击中心
                slap_r2 = center_r2 - amp_r2         # 扇下去时脚腕下压（鞭打）

                # 辅助函数：在两点之间线性插值
                def lerp(start, end, progress):
                    return start + (end - start) * progress

                def get_kinematics(local_prog):
                    # 0.0-0.6: 缓慢蓄力 (Windup)
                    # 0.6-0.7: 瞬间爆击 (Slap!)
                    # 0.7-1.0: 快速收回 (Recover to Park)
                    if local_prog < 0.6:
                        p = local_prog / 0.6
                        l0 = lerp(park_l0, windup_l0, p)
                        l2_off = lerp(park_l2_offset, windup_l2_offset, p)
                        r2 = lerp(center_r2, windup_r2, p)
                    elif local_prog < 0.7:
                        p = (local_prog - 0.6) / 0.1
                        l0 = lerp(windup_l0, slap_l0, p)
                        l2_off = lerp(windup_l2_offset, slap_l2_offset, p)
                        r2 = lerp(windup_r2, slap_r2, p)
                    else:
                        p = (local_prog - 0.7) / 0.3
                        l0 = lerp(slap_l0, park_l0, p)
                        l2_off = lerp(slap_l2_offset, park_l2_offset, p)
                        r2 = lerp(slap_r2, center_r2, p)
                    return l0, l2_off, r2

                if director < 0.5:
                    # Device A's turn
                    local_a = director / 0.5
                    l0_a, l2_off_a, r2_a = get_kinematics(local_a)

                    pos_a_l0 = l0_a
                    pos_a_l2 = center_l2 - (l2_off_a * l2_mult)
                    pos_a_r2 = r2_a
                    pos_a_r1 = center_a_r1 # 不加roll，纯靠L2和R2的力量

                    # B is parked
                    pos_b_l0 = park_l0
                    pos_b_l2 = center_l2 + (park_l2_offset * l2_mult)
                    pos_b_r2 = center_r2
                    pos_b_r1 = center_b_r1
                else:
                    # Device B's turn
                    local_b = (director - 0.5) / 0.5
                    l0_b, l2_off_b, r2_b = get_kinematics(local_b)

                    # A is parked
                    pos_a_l0 = park_l0
                    pos_a_l2 = center_l2 - (park_l2_offset * l2_mult)
                    pos_a_r2 = center_r2
                    pos_a_r1 = center_a_r1

                    pos_b_l0 = l0_b
                    pos_b_l2 = center_l2 + (l2_off_b * l2_mult)
                    pos_b_r2 = r2_b
                    pos_b_r1 = center_b_r1

                cmd_a_parts.extend([f"L0{clamp(pos_a_l0):04d}", f"L2{clamp(pos_a_l2):04d}", f"R2{clamp(pos_a_r2):04d}", f"R1{clamp(pos_a_r1):04d}"])
                cmd_b_parts.extend([f"L0{clamp(pos_b_l0):04d}", f"L2{clamp(pos_b_l2):04d}", f"R2{clamp(pos_b_r2):04d}", f"R1{clamp(pos_b_r1):04d}"])

            elif self.motion_mode == "glans_torture":'''

    if old_block_pattern.search(content):
        content = old_block_pattern.sub(new_block, content)
        with open('dual_osr_control.py', 'w') as f:
            f.write(content)
        print("V3 Slap patched.")
    else:
        print("Regex failed.")

patch()
