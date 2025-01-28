import vdif_data_frame_reader as fr
import vdif_properties as props
import vdif_datetime as dt
import vdif_analysing as anal
import vdif_correlating as corr
import matplotlib.pyplot as plt
import mmap
import numpy as np
from scipy.signal import stft
from tqdm import tqdm

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
    print("Processing Data (Fourier transforming)...")

    time = data[:, 0]
    values = data[:, 1]
    time_step = np.mean(np.diff(time))
    fft_result = np.fft.fft(values)
    fft_shifted_result = np.fft.fftshift(fft_result)
    fft_freq = np.fft.fftfreq(len(values), d=time_step)[::-1]
    amplitude = np.abs(fft_shifted_result)

    print("Plotting data...")

    plt.figure(figsize=(10, 6))
    plt.plot(fft_freq[:len(fft_freq)//2], amplitude[:len(amplitude)//2], label="Amplitude Spectrum")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude")
    plt.title("Fourier Transform: Amplitude vs. Frequency")
    plt.grid()
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.show(block=False)

def plot_data_waterfall_chunked(data, chunk_duration=50e-6, window_size=32, overlap=24, sampling_rate=None):
    """
    Slice the data into equally timed chunks, perform STFT on each chunk, compute a piecewise sum of all results,
    and create a waterfall plot.

    Parameters:
        data (numpy.ndarray): A 2D array where the first column is time and the second column is signal values.
        chunk_duration (float): Duration of each chunk in seconds.
        window_duration (float): Duration of the STFT window in seconds.
        overlap_duration (float): Duration of overlap between windows in seconds.
        sampling_rate (float, optional): Sampling rate of the data. If None, it is calculated from the time array.
    """
    print("Processing Data (Chunking and STFT transforming)...")

    time = data[:, 0]
    values = data[:, 1]

    if sampling_rate is None:
        time_step = np.mean(np.diff(time))
        sampling_rate = 1 / time_step

    # Convert durations to sample counts
    chunk_size = int(chunk_duration * sampling_rate)

    # Number of complete chunks
    total_chunks = len(values) // chunk_size

    # Initialize sum of STFT results
    summed_amplitude = None
    frequencies = None
    times = None

    # Process each chunk
    print("Starting chunk processing...")
    for chunk_idx in tqdm(range(total_chunks), desc="Processing Chunks"):
        start_idx = chunk_idx * chunk_size
        end_idx = start_idx + chunk_size
        chunk = values[start_idx:end_idx]

        # Perform STFT on the current chunk
        f, t, Zxx = stft(chunk, fs=sampling_rate, nperseg=window_size, noverlap=overlap)

        # Compute amplitude
        amplitude = np.abs(Zxx)

        amplitude = amplitude**3

        # Initialize or sum amplitudes
        if summed_amplitude is None:
            summed_amplitude = amplitude
            frequencies = f
            times = t + chunk_idx * chunk_duration
        else:
            summed_amplitude += amplitude

    print("Plotting data...")

    # Create the 2D plot
    plt.figure(figsize=(12, 8))
    plt.pcolormesh(times, frequencies, summed_amplitude, shading='gouraud', cmap='viridis')

    # Labeling
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.title("Chunked Waterfall Plot: Frequency vs. Time")
    plt.colorbar(label="Amplitude (Summed)")

    plt.tight_layout()
    plt.show(block=False)


def plot_data_waterfall(data, window_size=2048, overlap=0, sampling_rate=None):
    """
    Perform a Short-Time Fourier Transform (STFT) on the data and plot a 2D waterfall plot with color representing amplitude.
    
    Parameters:
        data (numpy.ndarray): A 2D array where the first column is time and the second column is signal values.
        window_size (int): The size of the window for STFT.
        overlap (int): The number of points overlapping between segments.
        sampling_rate (float, optional): Sampling rate of the data. If None, it is calculated from the time array.
    """
    print("Processing Data (STFT transforming)...")

    time = data[:, 0]
    values = data[:, 1]

    if sampling_rate is None:
        time_step = np.mean(np.diff(time))
        sampling_rate = 1 / time_step

    # Perform the Short-Time Fourier Transform (STFT)
    f, t, Zxx = stft(values, fs=sampling_rate, nperseg=window_size, noverlap=overlap)

    # Calculate amplitude
    amplitude = np.abs(Zxx)

    print("Plotting data...")

    plt.figure(figsize=(12, 8))
    
    # Create the 2D plot
    plt.pcolormesh(t, f, amplitude, shading='gouraud', cmap='viridis')

    # Labeling
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    # plt.ylim(1.99e6, 2.01e6)
    plt.title("Waterfall Plot: Frequency vs. Time")
    plt.colorbar(label="Amplitude")

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

def plot_frames_waterfall(file_path):
    """
    Plot Fourier Transform of the data retrieved from a VDIF file for a user-specified time range.
    """
    def plot_fourier(file_info, starting_header, data, start_seconds, end_seconds):
        plot_data_waterfall(data)

    anal.process_data_window(file_path, plot_fourier)

def plot_repeated_waterfall(file_path):
    """
    Plot Fourier Transform of the data retrieved from a VDIF file for a user-specified time range.
    """
    def plot_fourier(file_info, starting_header, data, start_seconds, end_seconds):
        plot_data_waterfall_chunked(data)

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

def auto_correlate(file_path):
    """
    Correlates a section of a vdif file with itself
    Args:
        file_path (_type_): Path to vdif file
    """    
    file_info = props.get_vdif_file_properties(file_path)

    def plot_fourier(file_info, starting_header, data, start_seconds, end_seconds):
        corr.plot_auto_correlation(data, file_info["sample_rate"], file_path)
    
    anal.process_data_window(file_path, plot_fourier)