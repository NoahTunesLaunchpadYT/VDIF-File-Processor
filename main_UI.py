"""
-------------------------------------------------------------------------------
File: main_UI.py
Author: Noah West
Date: 10/12/2024
Description: 
  This script provides a command-line user interface for processing and 
  analyzing VDIF (VLBI Data Interchange Format) files. It supports various 
  operations such as checking if a file is simple, retrieving properties, 
  and printing or plotting specific frames from the VDIF file.

License: 
  See LICENCE.txt for details on the licensing terms.

Dependencies:
  - vdif_plotting.py
  - vdif_printing.py
  - vdif_properties.py
  - vdif_is_simple.py
  - tqdm (for progress bars)
  - matplotlib (for plotting, if required in `vdif_plotting`)
  - Other custom VDIF utility modules as required

Usage:
  Run the script directly in a Python environment. Follow the instructions in
  the terminal.
-------------------------------------------------------------------------------
"""

import vdif_plotting as pl
import vdif_printing as pr
import vdif_properties as props
import vdif_is_simple as simp
import os

def print_welcome_message():
    print("\n")
    print("=" * 53)
    print(" Welcome to Noah's VDIF File Processor ")
    print("=" * 53)

def get_vdif_file_path():
    while True:
        file = input("Enter the path to the .vdif file: ")

        # If the file path is empty, use a default value
        if file == "":
            print("Using GSSR_SHADOW_43XLCP_181-0320_8M_UL_8558M_frch_L_0540-0650.vdif")
            file = "GSSR_SHADOW_43XLCP_181-0320_8M_UL_8558M_frch_L_0540-0650.vdif"
        
        # Check if the file has a type extension, if not, add ".vdif"
        if not os.path.splitext(file)[1]:  # No extension
            file += ".vdif"
        
        # Check if the extension is ".vdif", else inform the user
        elif os.path.splitext(file)[1].lower() != ".vdif":
            print("Invalid file type. Please enter a .vdif file.")
            continue

        # Try to open the file to ensure it exists and can be opened
        try:
            with open(file, 'rb') as f:
                # If it opens successfully, return the file path
                return file
        except IOError:
            print(f"Unable to open the file '{file}'. Please check the file path and try again.")

def display_commands():
    print("\nAvailable Commands:")
    print("  - is_simple       - Check if .vdif is simple, contiguous, and ordered")
    print("  - properties      - Get properties of a simple .vdif file")
    print("  - print_first     - Print the first frame (short format)")
    print("  - plot_first      - Plot the first frame")
    print("  - print_first_all - Print the first frame (full format)")
    print("  - print           - Print a range of times")
    print("  - plot            - Plot over a range of times")
    print("  - plot_fourier    - (coming soon) Plot the Forier transform of range of frame")
    print("  - plot_waterfall  - (coming soon) Plot up to a specific frame")
    print("  - exit            - (coming soon) Exit the program\n")

def get_command():
    return input("Enter your command (type 'help' for command list): ").strip().lower()


def main():
    print_welcome_message()

    vdif_file = get_vdif_file_path()

    while True:
        command = get_command()

        if command == "help":
            display_commands()
        elif command == "properties":
            props.print_vdif_file_properties(vdif_file)
        elif command == "print_first":
            pr.print_first_frame_short(vdif_file)
        elif command == "plot_first":
            pl.plot_first_frame(vdif_file)
        elif command == "print_first_all":
            pr.print_first_frame_all(vdif_file)
        elif command == "print":
            pr.print_frames(vdif_file)
        elif command == "plot":
            pl.plot_frames(vdif_file)
        elif command == "print_all":
            print("This option is coming soon.")
        elif command == "plot_all":
            print("This option is coming soon.")
        elif command == "plot_fourier":
            print("This option is coming soon.")
        elif command == "plot_waterfall":
            print("This option is coming soon.")
        elif command == "is_simple":
            simp.check_simplicity(vdif_file)
        elif command == "exit":
            print("Exiting the program. Goodbye!")
        else:
            print("Unknown command. Please try again.")

if __name__ == "__main__":
    main()
