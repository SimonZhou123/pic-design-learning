import gdsfactory as gf

# ========== MZI（马赫-曾德尔干涉仪） ==========

mzi = gf.components.mzi(
    length_x=10,       # 水平长度 (um)
    length_y=2,        # 垂直长度 (um)
    delta_length=10,   # 两臂长度差 (um) - 越长干涉越敏感
)

# 查看端口
print("=== MZI 端口 ===")
for port in mzi.ports:
    print(f"  {port.name}: ({port.x:.1f}, {port.y:.1f}), 角度{port.angle:.0f}度")

# 保存 GDS
mzi.write_gds('outputs/mzi_demo.gds')
print("\n已保存: outputs/mzi_demo.gds")
print("用 KLayout 打开看看吧！")
