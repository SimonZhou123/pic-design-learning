import gdsfactory as gf

# 创建一个芯片
c = gf.Component('first_chip')

# 画直波导 - 宽0.5um, 长20um
wg1 = c << gf.components.straight(length=20, width=0.5)
wg1.movex(-15)

# 画弯曲波导 - 半径5um, 转90度
bend = c << gf.components.bend_euler(radius=5, width=0.5)
bend.movex(10)

# 保存gds
c.write_gds('first_chip.gds')
print('first_chip.gds 已生成！用 KLayout 打开看看吧')
