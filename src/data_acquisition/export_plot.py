"""
Script to load profile, calculate derivatives, export forces, derivatives, metadata, and plot force, SSA, density.

Usage:
python export_plot.py <in-file> <out-dir>

Args:
in-file: the input .PNT binary file from the SMP
out-dir: (optional) the out directory to save derivative, force, metadata to. If
omitted no csvs are saved.

Returns:
None
"""

import os
import sys
from pathlib import Path

from snowmicropyn import Profile
from snowmicropyn import proksch2015
from snowmicropyn.parameterizations import calonne_richter2020
from matplotlib import pyplot as plt

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

def load_profile(in_profile, verbose = True):
    #this is the file path to upload the data
    p = Profile.load(in_profile) 

    if verbose:
        print(f'Timestamp: {p.timestamp}')
        print(f'SMP Serial Number: {p.smp_serial}')
        print(f'Coordinates: {p.coordinates}')
    
    #set marker points for mean and averages
    surface = p.detect_surface()
    ground = p.detect_ground()
    print(f'Surface detected at {surface}. Ground at {ground}')
    p.set_marker('surface', surface)
    p.set_marker('ground', ground)

    return p

def save_derivatives(p):

    p.export_samples(file = out_dir.joinpath(f'{p.name}_samples.csv')) 
    p.export_derivatives(file = out_dir.joinpath(f'{p.name}_derivatives.csv'), snowpack_only = False)
    p.export_meta(file = out_dir.joinpath(f'{p.name}_meta.csv'))
    # p.export_samples_niviz(export_settings = ExportSettings(), file = out_dir.joinpath(f'{p.name}_niviz.csv'))

def plot_derivatives(p, p2015):
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

if __name__ == '__main__':
    args = sys.argv
    assert len(args) == 2 or len(args) == 3

    in_fp = args[1]

    #this is the path of where the file is going to be saved along with the what you want the file name to be. Make sure to change prior to saving a new file
    out_dir = None
    if len(args) == 3:
        out_dir = Path(args[2])

    profile = load_profile(in_fp)
    #this is the SMP GitHub package to retrieve the SSA and density for each depth increment within the dataset
    derivatives = calonne_richter2020.calc(samples = profile.samples)

    if out_dir:
        save_derivatives(profile)
    
    plot_derivatives(profile, derivatives)
    
    