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
import vdif_file_search as fs
import os

def print_welcome_message():
    print("\n")
    print("=" * 53)
    print(" Welcome to Noah's VDIF File Processor ")
    print("=" * 53)

def display_commands():
    print("\nAvailable Commands:")
    print("  - is_simple       - Check if .vdif is simple, contiguous, and ordered")
    print("  - properties      - Get properties of a simple .vdif file")
    print("  - print_first     - Print the first frame (short format)")
    print("  - plot_first      - Plot the first frame")
    print("  - print_first_all - Print the first frame (full format)")
    print("  - print           - Print a range of times")
    print("  - plot            - Plot over a range of times")
    print("  - plot_fourier    - Plot the Forier transform of range of frame")
    print("  - plot_waterfall  - Plot a waterfall plot of amplitude given frquency and time")
    print("  - plot_repeated_waterfall  - Plot the resultant period sum of waterfall plots")
    print("  - exit            - Exit the program")
    print("  - clear           - clear the terminal\n")

def get_command():
    return input("Enter your command (type 'help' for command list): ").strip().lower()


def main():
    print_welcome_message()

    vdif_file = fs.get_vdif_file_path()

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
        elif command == "plot_fourier":
            pl.plot_frames_fourier(vdif_file)
        elif command == "plot_waterfall":
            pl.plot_frames_waterfall(vdif_file)
        elif command == "plot_repeated_waterfall":
            pl.plot_repeated_waterfall(vdif_file)
        elif command == "is_simple":
            simp.check_simplicity(vdif_file)
        elif command == "exit":
            print("Exiting the program. Goodbye!")
            break
        elif command == "clear":
            os.system('cls')
        else:
            print("Unknown command. Please try again.")

if __name__ == "__main__":
    main()
