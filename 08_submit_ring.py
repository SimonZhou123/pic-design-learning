"""
Ring Resonator FDTD Simulation - Submit to Cloud
环形谐振腔 FDTD 仿真：扫谱找共振谷，估算 Q 值和 FSR
"""
import os, sys

# Fix encoding BEFORE importing anything
# API Key loaded from system env var (不在脚本里明文写)
os.environ['SIMCLOUD_APIKEY'] = os.environ.get('SIMCLOUD_APIKEY', '')
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import numpy as np
import gdstk
import tidy3d as td
import tidy3d.web as web
import gdsfactory as gf
import warnings
warnings.filterwarnings('ignore')

from rich.console import Console
import logging
logging.getLogger('tidy3d').setLevel(logging.WARNING)

print("=" * 60)
print("Ring Resonator FDTD Simulation")
print("=" * 60)

# 1. 生成环形谐振腔版图（与 03_ring_resonator.py 相同参数）
print("\n1. Generating ring layout...")
wg_cross_section = gf.cross_section.cross_section(width=0.5, radius_min=5)
ring = gf.components.ring_single(
    radius=5, gap=0.2, length_x=10, length_y=2,
    cross_section=wg_cross_section,
)
ring.write_gds('ring_resonator.gds')
ports = {p.name: (p.x*1e-3, p.y*1e-3, p.angle) for p in ring.ports}
print(f"   Ports: o1{ports['o1'][:2]}  o2{ports['o2'][:2]}")

# 2. GDS 导入 Tidy3D
print("\n2. Importing GDS to Tidy3D...")
lib = gdstk.read_gds('ring_resonator.gds')
cell = lib.top_level()[0]
bb = cell.bounding_box()
cx, cy = (bb[0][0]+bb[1][0])/2, (bb[0][1]+bb[1][1])/2
sx, sy = bb[1][0]-bb[0][0], bb[1][1]-bb[0][1]

wg_geo = td.Geometry.from_gds(
    gds_cell=cell, axis=2, slab_bounds=(0, 0.22),
    gds_layer=1, gds_dtype=0, gds_scale=1.0,
)
print(f"   Layout size: {sx:.0f} x {sy:.0f} um")

# 3. 搭建仿真
print("\n3. Building simulation...")
si, sio2 = td.Medium(permittivity=3.48**2), td.Medium(permittivity=1.45**2)
L0 = 1.55  # 中心波长 um

# 扫谱范围 1500-1600nm，600 个点（0.17nm 分辨率，够分辨共振谷）
wl_span = np.linspace(1.50, 1.60, 600)
freqs = td.C_0 / wl_span

sim = td.Simulation(
    center=[cx, cy, 0], size=[sx+4, sy+4, 4],
    grid_spec=td.GridSpec.auto(min_steps_per_wvl=10, wavelength=L0),
    structures=[
        td.Structure(geometry=td.Box(center=[cx, cy, -1], size=[sx+20, sy+20, 2]), medium=sio2),
        td.Structure(geometry=wg_geo, medium=si, name="Si_wg"),
    ],
    sources=[td.ModeSource(
        center=[ports['o1'][0], ports['o1'][1], 0.11], size=[0, 3, 1.5],
        source_time=td.GaussianPulse(freq0=td.C_0/L0, fwidth=3e12),
        direction="+", mode_spec=td.ModeSpec(num_modes=1), mode_index=0,
    )],
    monitors=[
        td.FieldMonitor(center=[cx, cy, 0.11], size=[td.inf, td.inf, 0],
                        freqs=[td.C_0/L0], name="field"),
        td.ModeMonitor(center=[ports['o2'][0], ports['o2'][1], 0.11], size=[0, 3, 1.5],
                       freqs=freqs, mode_spec=td.ModeSpec(num_modes=1), name="output"),
    ],
    # 高 Q 环形腔需要较长运行时间让能量衰减
    run_time=2e-11, shutoff=1e-5,
    boundary_spec=td.BoundarySpec.all_sides(boundary=td.PML()),
)
print(f"   Grid: ~{int(sim.num_cells/1e6)}M cells, run_time 20ps")

# 4. 提交云端
print("\n4. Submitting to cloud...")
try:
    sim_data = web.run(sim, task_name="ring_resonator_fdtd", verbose=True)
except Exception as e:
    print(f"   Upload failed: {e}")
    print("   Check web UI for task status:")
    print(f"   https://tidy3d.simulation.cloud/workbench")
    exit()

# 5. 结果分析：找共振谷
print("\n5. Processing results...")
amps = sim_data["output"].amps
t = np.abs(amps.sel(mode_index=0, direction="+").values)**2
wl = wl_span * 1000  # nm

# 找局部极小值（共振谷）
from scipy.signal import find_peaks
peaks, props = find_peaks(-t, prominence=0.02)
print(f"   Found {len(peaks)} resonance dips")

# 估算每个共振的 Q 值和 FSR
dips = []
for i, idx in enumerate(peaks):
    # 用谷底两侧的半高点粗略估 FWHM
    half = (1 - t[idx])/2 + t[idx]
    left = wl[:idx][np.abs(t[:idx]-half).argmin()] if idx > 0 else wl[idx]
    right = wl[idx:][np.abs(t[idx:]-half).argmin()] if idx < len(wl)-1 else wl[idx]
    fwhm = abs(right-left)
    q = wl[idx]/fwhm if fwhm > 0 else float('inf')
    dips.append((wl[idx], t[idx], fwhm, q))
    print(f"   dip @ {wl[idx]:.1f}nm  T={t[idx]*100:.1f}%  FWHM~{fwhm:.2f}nm  Q~{q:.0f}")

fsr = None
if len(peaks) >= 2:
    fsr = wl[peaks[-1]] - wl[peaks[0]]
    print(f"   FSR (over {len(peaks)} dips): {fsr:.2f}nm")

# 6. 画图
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(wl, t, 'b-', lw=1.5)
for idx in peaks:
    ax.axvline(wl[idx], color='r', ls='--', alpha=0.4)
ax.set_xlabel('Wavelength (nm)'); ax.set_ylabel('Through transmission')
ax.set_title(f'Ring Resonator FDTD (R=5um, gap=0.2um) — {len(peaks)} dips, FSR~{fsr:.2f}nm' if fsr else f'Ring Resonator FDTD (R=5um, gap=0.2um) — {len(peaks)} dips')
ax.set_xlim(1500, 1600); ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('D:\\pic_design\\ring_spectrum.png', dpi=150)
print("\n6. Plot saved: ring_spectrum.png")
print(f"\n{'='*60} DONE {'='*60}")
