import os #System

from load import load_frames, get_reference_structure
from inputs import choose_shift_mode, get_reference_settings
from shift import get_structure_shift, apply_shift
from plotting import plot_surface_movie, prepare_visual_frames

#Define the main function to run imported functions
def main():

    # Optional reference surface for consistent substrate visualisation.
    # Ensure the reference and input structures have compatible cell dimensions, cell orientation, and ordering of the selected substrate atoms.
    # The reference is for visualisation.

    # Reference structure settings
    reference_symbols = ("Ni",) #This can be ignored or changed to None unless an element(s) is to be specified
    reference_folder = "Reference" #This can be ignored or changed to None unless a folder is to be specified
    reference_folder, reference_symbols = get_reference_settings(reference_symbols,reference_folder)

    # Load external reference structure if required
    reference_atoms = (get_reference_structure(reference_folder, repeat=(1, 1, 1)) if reference_folder is not None else None)

    # Find XDATCAR files
    trajectory_files = []

    for root, dirs, files in os.walk("."):

        # Exclude the reference folder and its contents
        if reference_folder is not None:
            reference_path = os.path.abspath(reference_folder)
            current_path = os.path.abspath(root)

            if os.path.commonpath((reference_path, current_path)) == reference_path:
                dirs.clear()
                continue

        # Find XDATCAR files
        if "XDATCAR" in files:
            trajectory_files.append(os.path.join(root, "XDATCAR"))

    if not trajectory_files:
        raise FileNotFoundError("No XDATCAR files were found outside the reference folder.")
    print(f"Found {len(trajectory_files)} XDATCAR files.")

    # Shift
    shift_mode = choose_shift_mode()

    # Figure
    figsize = (12, 6)
    dpi = 300
    fps = 2
    # Font
    font_family = "Times New Roman"
    font_size = 24
    title_size = 24
    font_weight = "bold"
    # Colours
    element_colors = {
        "Ni": "lightgray",
        "C": "black"
        }

    # Output directory
    output_folder = "Movies"
    os.makedirs(output_folder,exist_ok=True)

    # Process each trajectory
    for file in trajectory_files:
        # Load trajectory
        frames = load_frames(file,repeat=(1, 1, 1))
        if not frames:
            raise ValueError(f"No frames were found in '{file}'.")
        # Apply shift
        if shift_mode != 3:
            shift = get_structure_shift(frames[0],shift_mode)
            shifted_frames = [apply_shift(atoms,shift) for atoms in frames]
        else:
            shifted_frames = [atoms.copy() for atoms in frames]

        # Prepare visual frames using the external reference, if supplied
        visual_frames = prepare_visual_frames(shifted_frames,reference_atoms,reference_symbols)

        # Get folder name
        system_name = os.path.basename(os.path.dirname(file))
        # Output filename
        output_filename = os.path.join(output_folder,system_name + ".mp4")
        print(f"\nProcessing: {file}")
        print(f"Output: {output_filename}")

        # Generate movie
        plot_surface_movie(visual_frames,output_filename=output_filename,figsize=figsize,dpi=dpi,fps=fps,title_size=title_size,
                       font_size=font_size,font_family=font_family,font_weight=font_weight,element_colors=element_colors)

#Entry point/switch to run function
if __name__ == "__main__":
    #Load the main function
    main()