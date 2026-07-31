import gdsfactory as gf

# ========== 环形谐振腔 (Ring Resonator) ==========

# 使用 gdsfactory 内置的环形谐振腔组件
# 参数说明：
#   - radius:         环的半径 (um)
#   - gap:            直波导与环之间的耦合间隙 (um)
#   - length_x:       直波导水平段长度 (um)
#   - length_y:       垂直段长度 (um)
#   - cross_section:  波导截面（可指定宽度和最小弯曲半径）

# 自定义波导截面：宽 0.5μm，最小弯曲半径 5μm
wg_cross_section = gf.cross_section.cross_section(
    width=0.5,
    radius_min=5,    # 允许的最小弯曲半径
)

ring = gf.components.ring_single(
    radius=5,              # 环半径 5μm
    gap=0.2,               # 耦合间隙 0.2μm
    length_x=10,           # 直波导长度 10μm
    length_y=2,            # 垂直段长度 2μm
    cross_section=wg_cross_section,  # 波导截面
)

# 查看端口
print("=== 环形谐振腔端口 ===")
for port in ring.ports:
    print(f"  {port.name}: ({port.x:.1f}, {port.y:.1f}), 角度{port.angle:.0f}度")

# 保存 GDS
ring.write_gds('outputs/ring_resonator.gds')
print("\n已保存: outputs/ring_resonator.gds")
print("用 KLayout 打开看看吧！")
