# PIC Design Learning

硅基光电子（Silicon Photonics）PIC 设计学习仓库。

用 [gdsfactory](https://github.com/gdsfactory/gdsfactory) 画版图、[Tidy3D](https://www.flexcompute.com/tidy3d/) 做 FDTD 仿真，从零开始积累片上器件设计与仿真能力。

## 环境

- Python 3.x
- gdsfactory 8.x
- Tidy3D 2.x
- KLayout 0.30+

## 脚本列表

| # | 文件 | 内容 | 状态 |
|---|------|------|------|
| 01 | `01_straight_waveguide.py` | 直波导版图 | ✅ |
| 02 | `02_mzi_demo.py` | MZI（马赫-曾德尔干涉仪）版图 | ✅ |
| 03 | `03_ring_resonator.py` | 环形谐振腔版图 | ✅ 版图 / 🔄 待仿真 |
| 04 | `04_y_branch.py` | Y 分支（1×2 分束器）版图 | ✅ |
| 05 | `05_grating_coupler.py` | 光栅耦合器版图 + 变体 | ✅ |
| 06 | `06_mode_analysis.py` | 波导模式分析（有效折射率/模式场） | ✅ |
| 07 | `07_submit_mzi.py` | MZI 云端 FDTD 仿真（Tidy3D） | ✅ |

## 输出文件

- `*.gds` — 版图文件（KLayout 可打开）
- `mode_profiles.png` — 模式场分布图
- `mzi_spectrum.png` — MZI 透射谱仿真结果
- `simulation_data.hdf5` — Tidy3D 仿真原始数据

## 学习路线

1. **基础器件**：直波导 → Y 分支 → MZI → 环形谐振腔 → 光栅耦合器
2. **仿真验证**：Tidy3D FDTD 扫参（透射谱、Q 值、模式场）
3. **系统集成**：完整 PIC 版图（MZI 阵列 / 片上光谱仪 / AWG）
4. **作品集**：论文复现 + 开源贡献

## 参考

- gdsfactory 文档: <https://gdsfactory.github.io/>
- Tidy3D 文档: <https://docs.flexcompute.com/projects/tidy3d/>
