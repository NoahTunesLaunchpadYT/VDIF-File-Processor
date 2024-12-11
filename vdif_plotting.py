import vdif_data_frame_reader as fr
import vdif_properties as props
import vdif_datetime as dt
import vdif_analysing as anal
import matplotlib.pyplot as plt
import mmap
import numpy as np

def plot_data(data):
    """
    Plot data samples against time.
    """
    print("Plotting data...")

    plt.figure(figsize=(10, 5))
    plt.plot(data[:, 0], data[:, 1], label="Data Samples")
    plt.title("VDIF Frame Data")
    plt.xlabel("Time since epoch")
    plt.ylabel("Amplitude")
    plt.legend(loc="upper right")
    plt.grid()
    plt.show(block=False)


def plot_data_fourier(data):
    """
    Perform a Fourier Transform on the data and plot amplitude vs. frequency.
    """
    print("Plotting data...")

    time = data[:, 0]
    values = data[:, 1]
    time_step = np.mean(np.diff(time))
    fft_result = np.fft.fft(values)
    fft_shifted_result = np.fft.fftshift(fft_result)
    fft_freq = np.fft.fftfreq(len(values), d=time_step)
    amplitude = np.abs(fft_shifted_result)

    plt.figure(figsize=(10, 6))
    plt.plot(fft_freq[:len(fft_freq)//2], amplitude[:len(amplitude)//2], label="Amplitude Spectrum")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude")
    plt.title("Fourier Transform: Amplitude vs. Frequency")
    plt.grid()
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.show(block=False)

def plot_frames(file_path):
    """
    Plot data samples retrieved from a VDIF file for a user-specified time range.
    """
    def plot(file_info, starting_header, data, start_seconds, end_seconds):
        plot_data(data)

    anal.process_data_window(file_path, plot)


def plot_frames_fourier(file_path):
    """
    Plot Fourier Transform of the data retrieved from a VDIF file for a user-specified time range.
    """
    def plot_fourier(file_info, starting_header, data, start_seconds, end_seconds):
        plot_data_fourier(data)

    anal.process_data_window(file_path, plot_fourier)


def plot_first_frame(file_path):
    """
    Plot the first frame's data from a VDIF file.
    """
    file_info = props.get_vdif_file_properties(file_path)
    with open(file_path, 'rb') as file:
        mmapped_file = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)
        offset = 0
        _, data = fr.read_vdif_frame_data(mmapped_file, offset, file_info)
        plot_data(data)
