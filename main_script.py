from src import vdif_plotting as pl
from src import vdif_printing as prnt
from src import vdif_properties as props
from src import vdif_is_simple as simp
from src import vdif_file_search as fs
from src import predix_splitter as ps
from src import predix_reader as pr
from src import vdif_builder as build

def main():
    # Analysing a vdif file
    vdif_file = "vdif_sr8.0MHz_bw4.0MHz_pw2.5us_pp25.0us_dur10.0s_epoch48_start15572600s_snr10.0_randomPhase_dopplerShift.vdif"

    # Verify that the file is simple as defined in the vdif manual
    print("Checking simplicity")
    simp.check_simplicity(vdif_file)

    # Print the file properties
    print("Printing properties")
    props.print_vdif_file_properties(vdif_file)

    # Print the first frame of the vdif file in short
    print("Printing first frame")
    prnt.print_first_frame_short(vdif_file)

    # Plot the first frame
    print("Plotting first frame")
    pl.plot_first_frame(vdif_file)
    
    # Plot the discrete fourier transform over a time range 
    start_time = 15572600 # s since epoch
    end_time = 15572602 # s since epoch

    print("Plotting spectral plot")
    pl.plot_frames_fourier(vdif_file, start_time, end_time)

    # Plot the waterfall plot of the data over a time range
    print("Plotting waterfall")
    pl.plot_frames_waterfall(vdif_file, start_time, end_time)

    # Correlate the data with itself, hiding the trivial case
    print("Auto correlating")
    pl.auto_correlate(vdif_file, start_time, end_time)

    print("Correlating signal with chirp")
    # Correlate the data with a chirp signal
    bandwidth = 4e6 # Hz
    pulse_width = 2.5e-6 # s
    phase_offset = 0 # rad

    pl.correlate_chirp(vdif_file, start_time, end_time, bandwidth, pulse_width, phase_offset)

    # Compensate for the doppler effect using the predict file 
    # and then correlate with chirp
    predix_file = "2024mk.14f-13-43.8560MHz.s45.14-43.txt"

    pl.correlate_chirp_shifted(vdif_file, predix_file, start_time, end_time, bandwidth, pulse_width, phase_offset)

    build.plots_to_pdf()

    input("Press Enter to close graphs...")

    return

if __name__ == "__main__":
    main()
