import gdsfactory as gf

# ========== Y 分支 (Y-Branch) ==========

# 使用 gdsfactory 内置的 Y 分支组件
# 参数说明：
#   - length:      Y 分支总长度 (um)
#   - angle:       分支夹角 (度)
#   - width:       输入/输出波导宽度 (um)
#   - cross_section: 波导截面

# 自定义波导截面：宽 0.5μm，最小弯曲半径 5μm
wg_cross_section = gf.cross_section.cross_section(
    width=0.5,
    radius_min=5,    # 允许的最小弯曲半径
)

ybranch = gf.components.y_branch(
    length=20,              # 总长度 20μm
    angle=60,               # 分支夹角 60度
    width=0.5,              # 波导宽度 0.5μm
    cross_section=wg_cross_section,
)

# 查看端口
print("=== Y 分支端口 ===")
for port in ybranch.ports:
    print(f"  {port.name}: ({port.x:.1f}, {port.y:.1f}), 角度{port.angle:.0f}度")

# 保存 GDS
ybranch.write_gds('outputs/y_branch.gds')
print("\n已保存: outputs/y_branch.gds")
print("用 KLayout 打开看看吧！")
