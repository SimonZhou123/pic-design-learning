import gdsfactory as gf

# ========== 光栅耦合器 (Grating Coupler) ==========
# 使用 gf.components.grating_coupler_elliptical_te
# 基于椭圆聚焦型光栅，将光纤中的光耦合到芯片波导中
#
# 关键参数说明：
#   - taper_length:     锥形过渡区长度 (um)
#   - taper_angle:      锥形张角 (度)
#   - wavelength:       工作波长 (um)
#   - fiber_angle:      光纤倾斜角度 (度)
#   - grating_line_width: 光栅齿线宽 (um)
#   - n_periods:        光栅周期数
#   - big_last_tooth:   最后一个齿是否加粗
#   - spiked:           齿尖是否带尖刺（避免DRC错误）

# ============================================================
# 1. 基础光栅耦合器（默认参数）
# ============================================================
print("=" * 60)
print("1. 基础 TE 光栅耦合器（默认参数）")
print("=" * 60)

gc_default = gf.components.grating_coupler_elliptical_te()

print(f"  组件名: {gc_default.name}")
print(f"  端口数: {len(gc_default.ports)}")
print(f"  层数: {len(gc_default.layers)}")
print(f"  多边形数: {len(gc_default.get_polygons())}")

print("\n  === 端口信息 ===")
for port in gc_default.ports:
    print(f"    {port.name}: ({port.dx:.2f}, {port.dy:.2f}) um, 角度{port.angle:.1f}度, 宽度{port.width:.3f}um")

print(f"\n  组件信息: {gc_default.info}")

# ============================================================
# 2. 观察版图结构：光栅齿、波导过渡、光纤对准标记
# ============================================================
print("\n" + "=" * 60)
print("2. 版图结构分析")
print("=" * 60)

print("""
   ┌─────────────────────────────────────────────────────────┐
   │                   光纤 (Fiber)                           │
   │                      /                                  │
   │                     / 光纤角度 15°                       │
   │                    /                                    │
   │  ┌──────┬──────┬──/──┬──────┬──────┬──────┐            │
   │  │ 齿1  │ 齿2  │ /齿3 │ 齿4  │ 齿5  │ ...  │ ← 光栅齿  │
   │  └──────┴──────┴/────┴──────┴──────┴──────┘            │
   │              /                                          │
   │     ┌───────/────────┐                                  │
   │     │  锥形过渡区     │ ← taper_length=16.6um           │
   │     │  (taper)       │     taper_angle=40°              │
   │     └───────\\────────┘                                  │
   │              \\                                          │
   │    ───────────\\─────────── → 输出波导 (port o1)         │
   │                                                         │
   │  结构组成:                                              │
   │    ① 光栅齿 (Grating Teeth): 椭圆弧构成的周期性齿        │
   │       周期数 n_periods=30, 线宽 grating_line_width=0.343um│
   │    ② 锥形过渡 (Taper): 从单模波导展宽到光栅区           │
   │       长度 16.6um, 张角 40°                             │
   │    ③ 平板层 (Slab Layer): 光栅下方的平板波导层          │
   │    ④ 输出端口 (o1): 连接标准单模波导                    │
   └─────────────────────────────────────────────────────────┘
""")

# ============================================================
# 3. 调参数看视觉效果（多个变体对比）
# ============================================================
print("=" * 60)
print("3. 参数调优 - 多个变体对比")
print("=" * 60)

# --- 3a. 改变 taper_length（锥形长度） ---
print("\n--- 3a. 改变 taper_length（锥形长度） ---")
for length in [12, 16.6, 22]:
    gc = gf.components.grating_coupler_elliptical_te(taper_length=length)
    print(f"  taper_length={length:5.1f}um  →  端口: {len(gc.ports)}个, 多边形: {len(gc.get_polygons())}个")

# --- 3b. 改变 taper_angle（锥形张角） ---
print("\n--- 3b. 改变 taper_angle（锥形张角） ---")
for angle in [30, 40, 60]:
    gc = gf.components.grating_coupler_elliptical_te(taper_angle=angle)
    print(f"  taper_angle={angle:5.1f}°     →  端口: {len(gc.ports)}个, 多边形: {len(gc.get_polygons())}个")

# --- 3c. 改变 grating_line_width（光栅线宽） ---
print("\n--- 3c. 改变 grating_line_width（光栅线宽） ---")
for lw in [0.2, 0.343, 0.5]:
    gc = gf.components.grating_coupler_elliptical_te(grating_line_width=lw)
    print(f"  grating_line_width={lw:.3f}um →  端口: {len(gc.ports)}个, 多边形: {len(gc.get_polygons())}个")

# --- 3d. 改变 n_periods（光栅周期数） ---
print("\n--- 3d. 改变 n_periods（光栅周期数） ---")
for n in [10, 20, 30, 40]:
    gc = gf.components.grating_coupler_elliptical_te(n_periods=n)
    print(f"  n_periods={n:2d}           →  端口: {len(gc.ports)}个, 多边形: {len(gc.get_polygons())}个")

# --- 3e. 改变 fiber_angle（光纤角度） ---
print("\n--- 3e. 改变 fiber_angle（光纤角度） ---")
for fa in [8, 15, 25]:
    gc = gf.components.grating_coupler_elliptical_te(fiber_angle=fa)
    print(f"  fiber_angle={fa:5.1f}°     →  端口: {len(gc.ports)}个, 多边形: {len(gc.get_polygons())}个")

# --- 3f. big_last_tooth 效果 ---
print("\n--- 3f. big_last_tooth（最后一个大齿） ---")
gc_normal = gf.components.grating_coupler_elliptical_te(big_last_tooth=False)
gc_big = gf.components.grating_coupler_elliptical_te(big_last_tooth=True)
print(f"  big_last_tooth=False  →  多边形: {len(gc_normal.get_polygons())}个")
print(f"  big_last_tooth=True   →  多边形: {len(gc_big.get_polygons())}个")

# --- 3g. spiked 效果 ---
print("\n--- 3g. spiked（齿尖尖刺） ---")
gc_spiked = gf.components.grating_coupler_elliptical_te(spiked=True)
gc_no_spike = gf.components.grating_coupler_elliptical_te(spiked=False)
print(f"  spiked=True   →  多边形: {len(gc_spiked.get_polygons())}个")
print(f"  spiked=False  →  多边形: {len(gc_no_spike.get_polygons())}个")

# ============================================================
# 4. 创建一个包含多个变体的布局，方便对比观察
# ============================================================
print("\n" + "=" * 60)
print("4. 组合多个变体到同一芯片，方便对比")
print("=" * 60)

chip = gf.Component("grating_couplers")

# 放置默认版本
gc1 = chip << gf.components.grating_coupler_elliptical_te()
gc1.movex(0)
gc1.movey(0)
print(f"  位置1 (0, 0):      默认参数")

# 放置大张角版本
gc2 = chip << gf.components.grating_coupler_elliptical_te(taper_angle=60)
gc2.movex(0)
gc2.movey(-80)
print(f"  位置2 (0, -80):    taper_angle=60°")

# 放置短锥形版本
gc3 = chip << gf.components.grating_coupler_elliptical_te(taper_length=10)
gc3.movex(0)
gc3.movey(-160)
print(f"  位置3 (0, -160):   taper_length=10um")

# 放置少周期版本
gc4 = chip << gf.components.grating_coupler_elliptical_te(n_periods=15)
gc4.movex(0)
gc4.movey(-240)
print(f"  位置4 (0, -240):   n_periods=15")

# 放置大齿版本
gc5 = chip << gf.components.grating_coupler_elliptical_te(big_last_tooth=True)
gc5.movex(0)
gc5.movey(-320)
print(f"  位置5 (0, -320):   big_last_tooth=True")

# 放置无尖刺版本
gc6 = chip << gf.components.grating_coupler_elliptical_te(spiked=False)
gc6.movex(0)
gc6.movey(-400)
print(f"  位置6 (0, -400):   spiked=False")

# ============================================================
# 5. 保存 GDS
# ============================================================
print("\n" + "=" * 60)
print("5. 保存 GDS")
print("=" * 60)

gc_default.write_gds('grating_coupler.gds')
print("  已保存: grating_coupler.gds（单个默认光栅耦合器）")

chip.write_gds('grating_coupler_variants.gds')
print("  已保存: grating_coupler_variants.gds（6个变体对比）")

print("\n✅ 完成！用 KLayout 打开看看吧！")
print("  > 打开 grating_coupler.gds 查看单个光栅耦合器细节")
print("  > 打开 grating_coupler_variants.gds 对比不同参数效果")
