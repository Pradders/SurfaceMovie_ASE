# SurfaceMovie_ASE

A Python utility using the Atomic Simulation Environment (ASE) to load VASP `XDATCAR` trajectories, optionally shift atomic positions, and generate MP4 movies showing top and side views of the structures.

**Version 1.0.0 (v1.0.0)** — current release.

# Related projects

This repository is part of a collection of ASE-based tools for visualising VASP structures and analysing Bader charge changes.
* [StructurePlotting_ASE](https://github.com/Pradders/StructurePlotting_ASE) — General visualisation of VASP structures, including top and side views, atomic shifting and optional reference-surface alignment.
* [BaderTransition_atomplot](https://github.com/Pradders/BaderTransition_atomplot) — Visualisation of Bader charge differences between initial and final structures.
* [BaderTransition_catalyst](https://github.com/Pradders/BaderTransition_catalyst) — Catalyst-specific Bader charge analysis, comparing corresponding catalyst atoms even when the total number of atoms differs between structures.
* [NEBplotting_ASE](https://github.com/Pradders/NEBplotting_ASE) — General top-view visualisation of NEB structures calculated by VASP, including atomic shifting and optional reference-surface alignment.
* [SurfaceMovie_ASE](https://github.com/Pradders/SurfaceMovie_ASE) — Video visualisation of VASP structures, including top and side views, atomic shifting and optional reference-surface alignment.

# Overview

The code can:

- Locate `XDATCAR` files recursively in folders relative to `main.py`.
- Load all trajectory frames using ASE.
- Optionally shift atomic positions in the x and/or y directions.
- Apply either a common shift to all trajectories or an individual shift to each trajectory.
- Preview the first frame of a trajectory before determining a manual shift.
- Optionally use an external reference structure to provide a consistent substrate representation across trajectories.
- Retain the original calculated positions of adsorbates and other non-reference atoms when using a reference structure.
- Handle trajectories that do not contain any of the selected reference elements by warning and retaining the original structures.
- Check compatibility between the trajectory structures and the reference structure.
- Validate user-defined element symbols and colour values.
- Colour atoms according to their elements.
- Generate top and side views for each trajectory.
- Save each trajectory as an MP4 movie.

# Folder and file access

The trajectory files should be located in folders relative to `main.py`. The code searches recursively for files named `XDATCAR`.

An optional reference structure can be stored in a separate folder. For example:

```text
Reference/CONTCAR
System_1/XDATCAR
System_2/XDATCAR
```

The reference folder is excluded from the trajectory search. The reference folder is specified in `main.py` using:

```python
reference_folder = "Reference"
```

To disable the external reference structure:

```python
reference_folder = None
```

When the program starts, the user can choose whether to use the external reference folder or run without a reference structure. If no reference is selected, the reference folder and reference symbols are set to `None`.

When an external reference structure is used, the elements belonging to the reference substrate are specified using `reference_symbols`. For example, for a pure Ni substrate:

```python
reference_symbols = ("Ni",)
```

The reference structure is loaded from a `CONTCAR` or `POSCAR` file in the reference folder.

The reference element symbols must be valid chemical element symbols. Invalid symbols raise a `ValueError`.

The reference and trajectory structures must have compatible unit-cell dimensions and orientations. The selected reference atoms must also occur in the same order, element by element, in both structures. The code pairs the first occurrence of each selected element in the trajectory structure with the first occurrence in the reference structure, the second with the second, and so on.

This ordering is an assumption made by the reference-alignment procedure; the code does not independently identify the physical identity of each atom. If these assumptions are not satisfied, disable the external reference structure.

# Shifting

Structures can optionally be shifted in the x and y directions.

The shift is based on the **maximum covalent diameter** of the atoms in the structure. This is calculated from the largest covalent radius present in the structure:

```text
maximum diameter = 2 × maximum covalent radius
```

The user enters integer multiples of this diameter. For example:

```text
x = -1
y = +1
```

means that the entire structure is shifted:

- one maximum atomic diameter to the left in x
- one maximum atomic diameter upwards in y

The shift is determined from the first frame in the relevant trajectory scope. It is then applied consistently to the subsequent frames and is not recalculated during movie playback.

# Shift modes

When the program is run, the user selects one of three shifting options:

```text
1: SAME shift for ALL frames in ALL trajectories
2: MANUAL shift for EACH trajectory
3: NO shift
```

## Mode 1 — Same shift for all trajectories

The shift is determined using the first frame of the first trajectory. That same x/y shift is then applied to every frame of every trajectory processed by the program. Only the first frame of the first trajectory is previewed to determine the shift.

## Mode 2 — Manual shift for each trajectory

The first frame of each trajectory is individually previewed, and a separate x/y shift can be specified. The selected shift is then applied to every frame in that trajectory.

## Mode 3 — No shift

No translation is applied to the trajectory structures.

Reference alignment is a separate visual operation from the global x/y shift.

# Reference surface

An optional reference structure can be used to provide a consistent substrate representation across different trajectories. For example, when comparing several trajectories containing a Ni substrate, the Ni atoms in the individual calculated structures may have slightly different relaxed positions. The reference structure provides a common Ni surface for the visual representation.

The reference surface is used only for visualisation. The calculated positions of adsorbates and other non-reference atoms are retained.

The external reference is only applied when selected by the user. When no reference is selected, the trajectory structures are visualised without reference replacement.

## Reference structure processing

When a reference structure is provided, the program:

1. Loads the reference structure.
2. Checks that the reference structure is compatible with the trajectory structure.
3. Checks the selected reference elements and their atom counts.
4. Determines the periodic representation of the first frame that best matches the reference surface.
5. Applies the corresponding reference alignment consistently to the frames in that trajectory.
6. Uses the reference substrate atoms in the visual representation.
7. Retains the calculated positions of all non-reference atoms, such as H, C, or other adsorbates.

If none of the selected reference elements are present in a trajectory, the program prints a warning and visualises that trajectory without reference replacement. If some selected elements are present but the required element counts do not match, an error is raised.

The adsorbate atoms are not moved onto ideal reference adsorption sites. Therefore, small deviations of atoms such as H from ideal hollow, bridge, or top sites are retained in the visual representation. This is important because the calculated adsorbate geometry may result from interactions with other adsorbates, molecules, and the relaxed substrate. Automatically moving the adsorbates to ideal reference sites would change the calculated geometry. The reference surface should therefore be regarded as a visualisation aid for consistent substrate representation, rather than as the actual relaxed substrate geometry.

Periodic alignment assumes that the required translation can be handled by shifts of −1, 0, or +1 along the first two fractional coordinates.

The reference structure must contain the requested reference elements, and its unit-cell matrix must be compatible with that of the trajectory structure. If a valid reference structure cannot be loaded, a `FileNotFoundError` is raised rather than silently continuing without the requested reference.

# Colour coding

Atoms are coloured according to their chemical element. Specific colours can be defined in `main.py`. For example:

```python
element_colors = {
    "Ni": "lightgray",
    "C": "black"
}
```

User-defined element symbols and colour values are validated. Invalid chemical symbols or colour specifications raise a `ValueError`.

Elements not explicitly assigned a colour use the ASE/Jmol default colours. The atom colours are determined from the first frame and reused for the frames in the movie.

# Views

Two views are generated for each trajectory:

1. **Top View**
2. **Side View**

The top view uses:

```python
rotation="0x,0y,0z"
```

The side view uses:

```python
rotation="270x,0y,0z"
```

The two views are arranged horizontally by default.

The default figure size is:

```python
figsize = (12, 6)
```

The default resolution is:

```python
dpi = 300
```

The titles use Times New Roman, a font size of 24, and bold formatting by default.

# Movie settings

The frame rate is controlled by the `fps` argument in `main.py`. A lower frame rate makes each frame remain on screen for longer.

| Frame rate | Approximate display time per frame |
| ---: | ---: |
| 10 fps | 0.1 s |
| 5 fps | 0.2 s |
| 2 fps | 0.5 s |
| 1 fps | 1.0 s |

For example:

```python
fps = 2
```

The movie repeats during playback. The frame interval is determined from the selected frame rate.

# Movie saving

Movies are saved to the output directory specified in `main.py`.

The default output directory is:

```python
output_folder = "Movies"
```

The directory is automatically created if it does not already exist.

Each movie is saved as an MP4 file. The output filename is based on the name of the directory containing the corresponding `XDATCAR`, with the `.mp4` extension.

For example:

```text
Movies/
└── System_1.mp4
```

# Inputs

## Reference selection

When an external reference structure is configured, the program asks the user to select whether to use it:

```text
Select reference mode:
1: No reference
2: Use external reference folder
Enter 1 or 2:
```

The selected option must be confirmed before proceeding.

## Shift mode selection

When the program starts, the user is asked to select a shift mode:

```text
Select shift mode:

1: SAME shift for ALL frames in ALL trajectories
2: MANUAL shift for EACH trajectory
3: NO shift

Enter mode (1/2/3):
```

The selected option must be confirmed using the generic confirmation prompt:

```text
Accept this result/outcome? (y/n):
```

If an invalid value is entered, the program will ask again.

## Shifting inputs

For Modes 1 and 2, the program displays the relevant first frame before asking for the shift:

```text
Previewing structure.

Press Enter to close the figure...
```

The maximum covalent diameter is then displayed:

```text
Manual shift using max_radius = x.xxx Å
```

The user enters the x and y shift:

```text
Shift in x (multiples of diameter, negative = left, positive = right):
Shift in y (multiples of diameter, negative = down, positive = up):
```

The values must be integers.

# Python files

The code is separated into several files according to their purpose.

## `main.py`

Runs the overall workflow. It finds the `XDATCAR` files, selects the shift and reference settings, loads each trajectory, prepares the frames, and calls the movie-generation function.

## `inputs.py`

Contains functions for collecting user input:

```python
get_int()
confirm()
choose_shift_mode()
get_reference_settings()
```

## `load.py`

Contains functions for loading trajectory frames and reference structures, and checking reference compatibility:

```python
load_frames()
find_structure()
load_atoms()
check_reference_structure()
get_reference_structure()
```

## `shift.py`

Contains functions associated with shifting and previewing structures:

```python
max_radius()
view_cleanup()
build_shift()
apply_shift()
get_structure_shift()
```

## `plotting.py`

Contains functions for assigning atomic colours, preparing structures for visualisation, and generating movies:

```python
get_atom_colors()
prepare_visual_structure()
prepare_visual_frames()
plot_surface_movie()
plot_surface_views()
```

# Running the program

Run the main script from the directory containing the folders with your `XDATCAR` files:

```bash
python main.py
```

Select the requested shift and reference options when prompted. The generated MP4 movies will be written to the `Movies` directory.

# Example
See examples under the "Movies" and "Systems" folders. Two example figures are provided below.

[Watch example movie](Movies/Ni-trans_furfural.mp4)
<p align="center">
  <em>Video 1: Example video of furfural adsorbed on Ni(111).</em>
</p>

[Watch example movie](Movies/Ni-trans_furfural_H_1.mp4)
<p align="center">
  <em>Video 2: Example video of furfural adsorbed on Ni(111) co-adsorbed with an H atom.</em>
</p>

# Requirements

The code requires Python and the following packages:

- ASE
- NumPy
- Matplotlib

These can be installed using:

```bash
pip install ase numpy matplotlib
```

FFmpeg must also be installed separately and available on the system `PATH`. Matplotlib uses FFmpeg to write MP4 files.

To check that FFmpeg is available, run:

```bash
ffmpeg -version
```

The input trajectories must be in VASP `XDATCAR` format. If an external reference structure is used, it must be provided as a VASP `POSCAR` or `CONTCAR` file.
