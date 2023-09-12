import os
import sys
from pathlib import Path

import snowmicropyn
from snowmicropyn import Profile
from snowmicropyn import proksch2015
from matplotlib import pyplot as plt

args = sys.argv
assert len(args) == 2 or len(args) == 3 or len(args) == 4

in_profile = args[1]

#this is the path of where the file is going to be saved along with the what you want the file name to be. Make sure to change prior to saving a new file
out_dir = None
if len(args) == 3:
    out_dir = Path(args[2])

out_fp = None
if len(args) == 4:
    out_fp = Path(args[3])

# class of export settings for NiVIZ
class ExportSettings:
    export_data_thinning = 10000
    export_slope_angle = 0.0
    export_stretch_factor = 1.0

def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)

#this is the file path to upload the data
p = Profile.load(in_profile) 

print(f'Timestamp: {p.timestamp}')
print(f'SMP Serial Number: {p.smp_serial}')
print(f'Coordinates: {p.coordinates}')

#this is the SMP GitHub package to retrieve the SSA and density for each depth increment within the dataset
p2015 = proksch2015.calc(p.samples)

#set marker points for mean and averages
surface = p.detect_surface()
ground = p.detect_ground()
print(f'Surface detected at {surface}. Ground at {ground}')
p.set_marker('surface', surface)
p.set_marker('ground', ground)
sample_start = p.marker('surface')
sample_end = p.marker('ground')
sample = p2015[p2015.distance.between(sample_start, sample_end)]

#this saves the data to a CSV using the "path" previously defined
if out_dir or out_fp:
    # p.export_samples(file = out_dir.joinpath(f'{p.name}_samples.csv')) 
    if not out_fp:
        out_fp = out_dir.joinpath(f'{p.name}_derivatives.csv')
    p.export_derivatives(file = out_fp, snowpack_only = False, parameterization='CR2020')
    print('here')

    # p.export_meta(file = out_dir.joinpath(f'{p.name}_meta.csv'))
    # p.export_samples_niviz(export_settings = ExportSettings(), file = out_dir.joinpath(f'{p.name}_niviz.csv'))

#prints the mean density and SSA for sample
print('Mean SSA within sample: {:.1f} m^2/m^3'.format(sample.P2015_ssa.mean()))
print('Mean density within sample: {:.1f} kg/m^3'.format(sample.P2015_density.mean()))

fig, ax = plt.subplots()
fig.subplots_adjust(right=0.75)
# Plot distance on x and samples on y axis
ln1 = ax.plot(p.samples.distance, p.samples.force, label = 'Force', color = 'C0')
# Plot derivatives
ax2 = plt.twinx(ax)
ln3 = ax2.plot(p2015.distance, p2015.P2015_density, label = 'Density', color = 'C1')

ax3 = plt.twinx(ax)
ax3.spines["right"].set_position(("axes", 1.2))
ln2 = ax3.plot(p2015.distance, p2015.P2015_ssa, label = 'SSA', color = 'C2')
make_patch_spines_invisible(ax3)
ax3.spines["right"].set_visible(True)

# Prettify our plot a bit
plt.title(p.name)
ax.set_xlabel('Depth [mm]')
ax.set_ylabel('Force [N]')
ax2.set_ylabel('Density (kg/m3)')
ax3.set_ylabel("SSA (m2/m3)")

ax.yaxis.label.set_color(ln1[0].get_color())
ax2.yaxis.label.set_color(ln3[0].get_color())
ax3.yaxis.label.set_color(ln2[0].get_color())

# added these three lines
lns = ln1+ln2+ln3
labs = [l.get_label() for l in lns]
ax.legend(lns, labs, loc=0)

# Show interactive plot with zoom, export and other features
plt.show()