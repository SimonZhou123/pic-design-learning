"""
MZI FDTD Simulation - Submit to Cloud
Handles Windows encoding issues
"""
import os, sys

# Fix encoding BEFORE importing anything
# API Key loaded from system env var (贾维斯已配置，不在脚本里明文写)
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

# Silence Rich Windows rendering
from rich.console import Console
import logging
logging.getLogger('tidy3d').setLevel(logging.WARNING)

print("=" * 60)
print("MZI FDTD Simulation")
print("=" * 60)

# 1. Load MZI layout
print("\n1. Loading MZI GDS...")
mzi = gf.components.mzi(length_x=10, length_y=2, delta_length=10)
mzi.write_gds('outputs/mzi_demo.gds')
ports = {p.name: (p.x*1e-3, p.y*1e-3, p.angle) for p in mzi.ports}

# 2. Import GDS
print("\n2. Importing GDS to Tidy3D...")
lib = gdstk.read_gds('outputs/mzi_demo.gds')
cell = lib.top_level()[0]
bb = cell.bounding_box()
cx, cy = (bb[0][0]+bb[1][0])/2, (bb[0][1]+bb[1][1])/2
sx, sy = bb[1][0]-bb[0][0], bb[1][1]-bb[0][1]

wg_geo = td.Geometry.from_gds(
    gds_cell=cell, axis=2, slab_bounds=(0, 0.22),
    gds_layer=1, gds_dtype=0, gds_scale=1.0,
)
print(f"   MZI size: {sx:.0f} x {sy:.0f} um")

# 3. Build simulation
print("\n3. Building simulation...")
si, sio2 = td.Medium(permittivity=3.48**2), td.Medium(permittivity=1.45**2)
L0 = 1.55
sim = td.Simulation(
    center=[cx, cy, 0], size=[sx+4, sy+4, 4],
    grid_spec=td.GridSpec.auto(min_steps_per_wvl=10, wavelength=L0),
    structures=[
        td.Structure(geometry=td.Box(center=[cx, cy, -1], size=[sx+20, sy+20, 2]), medium=sio2),
        td.Structure(geometry=wg_geo, medium=si, name="Si_wg"),
    ],
    sources=[td.ModeSource(
        center=[ports['o1'][0], ports['o1'][1], 0.11], size=[0, 3, 1.5],
        source_time=td.GaussianPulse(freq0=td.C_0/L0, fwidth=2.5e12),
        direction="+", mode_spec=td.ModeSpec(num_modes=1), mode_index=0,
    )],
    monitors=[
        td.FieldMonitor(center=[cx, cy, 0.11], size=[td.inf, td.inf, 0],
                       freqs=[td.C_0/L0], name="field"),
        td.ModeMonitor(center=[ports['o2'][0], ports['o2'][1], 0.11], size=[0, 3, 1.5],
                       freqs=np.linspace(td.C_0/1.60, td.C_0/1.50, 300),
                       mode_spec=td.ModeSpec(num_modes=1), name="output"),
    ],
    run_time=3e-12, shutoff=1e-5,
    boundary_spec=td.BoundarySpec.all_sides(boundary=td.PML()),
)
print(f"   Grid: ~{int(sim.num_cells/1e6)}M cells")

# 4. Submit
print("\n4. Submitting to cloud...")
try:
    sim_data = web.run(sim, task_name="mzi_demo", verbose=True)
except Exception as e:
    print(f"   Upload failed: {e}")
    print("   Check web UI for task status:")
    print(f"   https://tidy3d.simulation.cloud/workbench")
    exit()

# 5. Results
print("\n5. Processing results...")
amps = sim_data["output"].amps
s21 = np.abs(amps.sel(mode_index=0, direction="+").values)**2
wl = td.C_0 / np.linspace(td.C_0/1.60, td.C_0/1.50, 300)
er = 10*np.log10(np.max(s21)/max(np.min(s21), 1e-10))
print(f"   ER: {er:.1f} dB | Max T: {np.max(s21)*100:.1f}%")

# 6. Plot
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(wl*1000, s21, 'b-', lw=2)
ax.set_xlabel('Wavelength (nm)'); ax.set_ylabel('Transmission')
ax.set_title(f'MZI FDTD (ER={er:.1f} dB)')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('outputs/mzi_spectrum.png', dpi=150)

fig2, ax = plt.subplots(figsize=(10, 5))
ax.plot(wl*1000, s21, 'b-', label='FDTD', lw=2)
ax.plot(wl*1000, np.cos(np.pi*2.4182*10/wl)**2, 'g--', label='Theory', alpha=0.7)
ax.legend(); ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('outputs/mzi_comparison.png', dpi=150)

print("\n6. Plots saved: outputs/mzi_spectrum.png, outputs/mzi_comparison.png")
print(f"\n{'='*60} DONE {'='*60}")
