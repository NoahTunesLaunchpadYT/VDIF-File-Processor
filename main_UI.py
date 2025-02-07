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
  - Pillow
  - numpy
  - Other custom VDIF utility modules as required

Usage:
  Run the script directly in a Python environment. Follow the instructions in
  the terminal.
-------------------------------------------------------------------------------
"""

from src import vdif_plotting as pl
from src import vdif_printing as prnt
from src import vdif_properties as props
from src import vdif_is_simple as simp
from src import vdif_file_search as fs
from src import predix_splitter as ps
from src import predix_reader as pr
from src import vdif_builder as build
import os

def print_welcome_message():
    print("\n")
    print("=" * 53)
    print(" Welcome to Noah's VDIF File Processor ")
    print("=" * 53)

def get_mode():
    command = input("Enter 'analyser' to use the VDIF analyser, or 'builder' to use the VDIF builder: ")
    if not command:
        command = 'analyser'
    return command

def display_commands():
    print("\nAvailable Commands:")
    print("  - help            - Brings up this menu")
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
    print("  - auto_correlate  - Correlate a signal with itself using match filtering")
    print("  - correlate_chirp - Correlates the signal with a chirp ")
    print("  - correlate_chirp_shifted - Doppler Compensates using a PREDIX file, then Correlates the signal with a chirp")
    print("  - exit            - Exit the program")
    print("  - clear           - clear the terminal\n")

def display_build_commands():
    print("\nAvailable Commands:")
    print("  - help            - Brings up this menu")
    print("  - split_predix_file - Splits a PREDIX file by its tables")
    print("  - plot_predix_file  - Plots each of the columns in a split PREDIX file")
    print("  - generate_vdif   - Creates a VDIF file of a modelled linear FM signal.")
    print("  - split_vdif      - (Coming soon) Splits a vdif file given two time stamps")
    print("  - plots_to_pdf    - Convert all the plots in the plots folder to a pdf")
    print("  - exit            - Exit the program")
    print("  - clear           - clear the terminal\n")

def get_command():
    return input("Enter your command (type 'help' for command list): ").strip().lower()

def main():
    while True:
        print_welcome_message()
        mode = get_mode()

        if mode == "analyser":
            process_vdif_files()
        elif mode == "builder":
            build_vdif_files()
        elif mode == "clear":
            os.system('cls')
        else:
            print("Something went wrong")

def build_vdif_files():
    while True:
        print("\n  ---- VDIF BUILDER ----")
        command = get_command()

        if command == "help":
            display_build_commands()
        elif command == "split_predix_file":
            ps.split_predix_UI()
        elif command == "plot_predix_file":
            pr.plot_predix_file()
        elif command == "generate_vdif":
            build.build_vdif()
        elif command == "split_vdif":
            build.split_vdif()
        elif command == "plots_to_pdf":
            build.plots_to_pdf()
        elif command == "clear":
            os.system('cls')
        elif command == "exit":
            print("Exiting the builder. Returning to main menu.")
            break
        else:
            print("Unknown command. Please try again.")

def process_vdif_files():
    vdif_file = fs.get_vdif_file_path()

    while True:
        print("\n  ---- VDIF ANALYSER ----")
        command = get_command()

        if command == "help":
            display_commands()
        elif command == "is_simple":
            simp.check_simplicity(vdif_file)
        elif command == "properties":
            props.print_vdif_file_properties(vdif_file)
        elif command == "print_first":
            prnt.print_first_frame_short(vdif_file)
        elif command == "plot_first":
            pl.plot_first_frame(vdif_file)
        elif command == "print_first_all":
            prnt.print_first_frame_all(vdif_file)
        elif command == "print":
            prnt.print_frames(vdif_file)
        elif command == "plot":
            pl.plot_frames(vdif_file)
        elif command == "plot_fourier":
            pl.plot_frames_fourier(vdif_file)
        elif command == "plot_waterfall":
            pl.plot_frames_waterfall(vdif_file)
        elif command == "plot_repeated_waterfall":
            pl.plot_repeated_waterfall(vdif_file)
        elif command == "auto_correlate":
            pl.auto_correlate(vdif_file)
        elif command == "correlate_chirp":
            pl.correlate_chirp(vdif_file)
        elif command == "correlate_chirp_shifted":
            pl.correlate_chirp_shifted(vdif_file)
        elif command == "exit":
            print("Exiting the analyser. Returning to main menu.")
            break
        elif command == "clear":
            os.system('cls')
        else:
            print("Unknown command. Please try again.")

if __name__ == "__main__":
    main()
