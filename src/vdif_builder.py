import numpy as np
from scipy.interpolate import interp1d
from datetime import datetime
import struct
try:
    import predix_splitter as ps
    import predix_reader as pr
    import vdif_datetime as dt
except:
    from src import predix_splitter as ps
    from src import predix_reader as pr
    from src import vdif_datetime as dt
from tqdm import tqdm
from PIL import Image
import os

def create_vdif_file(data_array, sample_rate, filename, 
                    start_seconds_from_epoch=0.0, epoch=48, station_id=0,
                    bits_per_sample=8):
    """
    Creates a single-channel VDIF file from a numpy array.
    
    Args:
        data_array (np.ndarray): Input data array (int8 or int16)
        sample_rate (int): Samples per second (e.g., 8e6)
        filename (str): Output filename
        start_seconds_from_epoch (float): Start time in seconds since reference epoch
        epoch
        station_id (int): 16-bit station identifier
        bits_per_sample (int): 8 or 16 bits per sample
    """
    # Validate parameters
    if bits_per_sample not in [8, 16]:
        raise ValueError("Only 8 or 16 bits per sample supported")
    if data_array.dtype not in [np.int8, np.int16]:
        raise ValueError("Data array must be int8 or int16 type")

    samples_per_frame = sample_rate // 1000  # Samples per millisecond
    bytes_per_sample = bits_per_sample // 8
    frame_data_bytes = samples_per_frame * bytes_per_sample
    frame_length = (32 + frame_data_bytes) // 8  # VDIF frame length in 8-byte units

    # Calculate number of complete frames
    num_frames = int(len(data_array) // samples_per_frame)
    if num_frames == 0:
        raise ValueError("Data array too short for even one complete frame")

    # Calculate initial time components
    initial_seconds = int(start_seconds_from_epoch)
    initial_frame_offset = int(round((start_seconds_from_epoch - initial_seconds) * 1000))

    with open(filename, 'wb') as f:
        for i in range(num_frames):
            # Calculate time parameters
            total_frame = initial_frame_offset + i
            seconds = initial_seconds + (total_frame // 1000)
            frame_number = total_frame % 1000

            # Build header components
            header = struct.pack(
                '<IIII',
                # Word 0: Seconds from epoch (30 bits)
                seconds & 0x3FFFFFFF,
                # Word 1: Reference epoch (6 bits) | Frame number (24 bits)
                (epoch << 24) | (frame_number & 0xFFFFFF),  # Reference epoch = 0
                # Word 2: Version (3) | Log2 channels (0) | Frame length (24)
                (1 << 29) | (0 << 24) | frame_length,  # Version=1, 1 channel
                # Word 3: Data type | Bits/sample | Thread ID | Station ID
                (0 << 31) | 
                ((bits_per_sample-1) << 26) | 
                (0 << 16) |  # Thread ID = 0
                (station_id & 0xFFFF)
            )
            
            # Extended header (16 bytes of zeros)
            full_header = header + b'\x00' * 16

            # Convert data to VDIF format
            chunk = data_array[i*samples_per_frame:(i+1)*samples_per_frame]
            if bits_per_sample == 8:
                vdif_data = (chunk + 128).astype(np.uint8).tobytes()
            else:  # 16-bit
                vdif_data = (chunk + 32768).astype(np.uint16).tobytes()

            # Write frame to file
            f.write(full_header)
            f.write(vdif_data)

def generate_fm_chirp(B, chirp_length, signal_period, sample_rate, total_duration, signal_portion, randomise_phase=False):
    """
    Generate an FM chirp signal with specified parameters, preallocating the array.
    
    Args:
        B (float): Bandwidth (Hz).
        chirp_length (float): Duration of one chirp (seconds).
        signal_period (float): Time between chirps (seconds).
        sample_rate (float): Sampling rate (samples/second).
        total_duration (float): Total duration of the signal (seconds).
        signal_portion (float): Scaling factor for signal amplitude.
        randomise_phase (bool): Randomize phase for each chirp (default: False).
    
    Returns:
        np.ndarray: Generated signal (complex-valued).
    """

    print(f"Chirp Length: {chirp_length} s")
    print(f"Signal Period: {signal_period} s")
    # Calculate total samples and preallocate array
    total_samples = int(total_duration * sample_rate)
    signal = np.zeros(total_samples, dtype=np.complex128)
    
    # Time vector for one chirp
    t_chirp = np.linspace(0, chirp_length, int(chirp_length * sample_rate), endpoint=False)
    chirp_samples = len(t_chirp)
    
    current_sample = 0  # Track the current sample index
    num_chirps = int(total_duration / signal_period)  # Estimate the number of chirps
    
    # Add a progress bar
    with tqdm(total=num_chirps, desc="Generating FM chirp", unit="chirp") as pbar:
        while True:
            # Calculate next chirp start
            next_chirp_sample = current_sample + int((signal_period - chirp_length) * sample_rate)
            
            # Add gap (zeros) between current_sample and next_chirp_sample
            gap_start = current_sample
            gap_end = min(next_chirp_sample, total_samples)
            gap_length = gap_end - gap_start
            if gap_length > 0:
                signal[gap_start:gap_end] = 0
            
            # Add chirp if there's space
            chirp_start = gap_end
            chirp_end = chirp_start + chirp_samples
            if chirp_end <= total_samples:
                # Generate random phase if needed
                phase = np.random.uniform(0, 2 * np.pi) if randomise_phase else 0
                chirp = np.exp(1j * (np.pi * (B / chirp_length) * t_chirp**2 + phase))
                
                # Insert chirp into the signal
                signal[chirp_start:chirp_end] = chirp
                current_sample = chirp_end
                pbar.update(1)  # Update progress bar
            else:
                break  # Exit loop if no space for another chirp
    
    return (signal.real * 63 * signal_portion).astype(np.int8)

def add_noise(signal, noise_portion):
    """
    Add Gaussian noise to a signal without causing overflow.

    Args:
        signal (np.ndarray): Input signal (int8).
        noise_level (float): Standard deviation of the noise.

    Returns:
        np.ndarray: Noisy signal (int8).
    """
    # Scale signal to leave room for noise
    scaled_signal = signal.astype(np.float32) / 2.0

    # Generate Gaussian noise
    noise = np.random.normal(0, noise_portion*63, size=scaled_signal.shape).astype(np.int8)

    # Add noise and clip to valid range
    noisy_signal = scaled_signal + noise
    noisy_signal = np.clip(noisy_signal, -128, 127)

    # Scale back to int8
    return (noisy_signal).astype(np.int8)

def generate_rtt_from_predix(epoch, seconds_since_epoch, duration, sample_rate, predix_file=None):
    
    if not predix_file:
        predix_file = ps.find_and_select_txt_file()
        
    predix_data = pr.extract_predix_data(predix_file)
    
    if not "RTT" in predix_data["column_labels"]:
        print("This predix file has no RTT column. Doppler shift can not be simulated without RTT.")
        return
    else:
        RTT_index = predix_data["column_labels"].index("RTT")
        
        # Extract columns using list comprehensions
        time_column = [row[0] for row in predix_data["data"]]  # First column (time)
        rtt_column = [row[RTT_index] for row in predix_data["data"]]  # RTT column

    # Convert epoch to a numpy.datetime64 object (epoch is the number of half years since 2000)
    epoch_start = np.datetime64(datetime(2000, 1, 1), 's')  # Convert to numpy.datetime64 with second resolution
    half_year_delta = np.timedelta64(6, 'M').astype('timedelta64[s]')  # Convert 6 months to seconds
    epoch_time = epoch_start + epoch * half_year_delta

    # Parse the time_column into datetime objects
    timestamps = [datetime.strptime(t, "%Y %b %d %H:%M:%S") for t in time_column]

    # Convert timestamps to numpy.datetime64 with second resolution
    timestamps_np = np.array([np.datetime64(t, 's') for t in timestamps])

    # Convert timestamps to seconds since the epoch
    times_since_epoch = (timestamps_np - epoch_time).astype('float64')

    # Create an interpolation function for the RTT values
    rtt_interp = interp1d(times_since_epoch, rtt_column, kind='linear', fill_value="extrapolate")

    # Generate the time array for the desired duration and sample rate
    start_time = seconds_since_epoch
    end_time = start_time + duration
    time_array = np.arange(start_time, end_time, 1/sample_rate)

    # Interpolate the RTT values for the time array
    rtt_values = rtt_interp(time_array)

    return rtt_values

def doppler_shift(data, rtt, sample_rate):
    """
    Applies Doppler shift to a signal using pre-interpolated RTT values.
    Uses a sneaky trick to shift the delayed time function to start at t=0.

    Args:
        data (np.array): Input signal (no time bearing).
        rtt (np.array): Pre-interpolated RTT values (in seconds).
        sample_rate (float): Sample rate of the input signal (in Hz).

    Returns:
        np.array: Doppler-shifted signal (received array).
    """
    # Time step for the input signal
    dt = 1 / sample_rate

    # Generate time array for the input signal
    signal_time = np.arange(len(data)) * dt

    # Shift the RTT values to start at t=0
    rtt_min = np.min(rtt)
    rtt_shifted = rtt - rtt_min

    # Initialize the received array with zeros (size defined by rtt array)
    received_array = np.zeros(len(rtt))

    # Loop over each time step in the RTT array with a progress bar
    print("Doppler Shifting...")
    for i, rtt_value in tqdm(enumerate(rtt_shifted), total=len(rtt_shifted)):
        # Calculate the delayed time (shifted to start at t=0)
        delayed_time = signal_time[i] - rtt_value

        # Compute the delayed index using flooring
        delayed_index = int(delayed_time / dt)

        # Skip if delayed index is out of bounds
        if delayed_index >= len(data) or delayed_index < 0:
            continue

        # Assign the value from data to received_array
        received_array[i] = data[delayed_index]

    return received_array.astype(np.int8)

def inverse_doppler_shift(received_data, rtt, sample_rate):
    """
    Reconstructs the transmitted signal from a received signal by reversing the Doppler shift.

    Args:
        received_data (np.array): Received signal affected by Doppler shift.
        rtt (np.array): RTT values (in seconds) at each received time step.
        sample_rate (float): Sample rate of the signal (in Hz).

    Returns:
        np.array: Reconstructed transmitted signal.
    """
    dt = 1 / sample_rate  # Time step for the signal

    received_time = np.arange(len(received_data)) * dt  # Time array for received signal

    # Shift RTT so that it starts from zero
    rtt_min = np.min(rtt)
    rtt_shifted = rtt - rtt_min

    print("Compensating for Doppler shifting...")

    # Compute transmitted time
    transmitted_time = received_time - rtt_shifted

    # Initialize transmitted signal
    transmitted_array = np.zeros(len(received_data), dtype=received_data.dtype)

    # Find valid indices
    valid_indices = (transmitted_time >= 0) & (transmitted_time < received_time[-1])

    # Get valid time and data
    valid_transmitted_time = transmitted_time[valid_indices]
    valid_received_data = received_data[valid_indices]

    # Compute integer indices
    transmitted_indices = np.round(valid_transmitted_time / dt).astype(int)

    # Ensure no out-of-bounds indices
    transmitted_indices = np.clip(transmitted_indices, 0, len(received_data) - 1)

    # Process with progress bar
    for i in tqdm(range(len(transmitted_indices)), desc="Reconstructing signal", unit="samples"):
        transmitted_array[transmitted_indices[i]] = valid_received_data[i]

    return transmitted_array.astype(np.int8)

def build_vdif():
    print("Welcome to the VDIF builder interface.")

    bits_per_sample = 8 # Other values are untested
    sample_rate = int(input("Enter samplerate in Hz (default: 8e6): ") or 8e6)  # 8 MHz
    bandwidth = float(input("Enter bandwidth in Hz (default: 4e6): ") or 4e6)  # 4 MHz
    pulse_width = float(input("Enter pulse width in seconds (default: 2.5e-6): ") or 2.5e-6)
    pulse_period = float(input("Enter the period of the pulse signal in seconds (default: 25e-6): ") or 25e-6)
    duration = float(input("Enter duration in seconds (default: 10): ") or 10)
    epoch = int(input("Enter the epoch number (half years since 2000, default: 48): ") or 48)
    start_time_str = input("Enter the start time (YYYY-MM-DD HH:MM:SS.sss or seconds since epoch, default 15572600): ") or "15572600"
    seconds_since_epoch = dt.parse_time_input(start_time_str, epoch)
    SNR = float(input("Enter the signal to noise ratio (default = 1) signal/noise = ") or 1)
    signal_portion = SNR / (SNR + 1)
    noise_portion = 1 / (SNR + 1)
    
    randomise_phase = input("Would you like to randomise the phase of the chirp? (Y/n, default Y): ").strip().lower() != "n"
    add_doppler_shift = input("Would you like to simulate doppler shift with a PREDIX file? (Y/n, default Y): ").strip().lower() != "n"
    
    if add_doppler_shift:
        rtt = generate_rtt_from_predix(epoch, seconds_since_epoch, duration, sample_rate)

    data = generate_fm_chirp(bandwidth, pulse_width, pulse_period, sample_rate, duration+1, signal_portion, randomise_phase)
    data = add_noise(data, noise_portion)
        
    if add_doppler_shift:
        data = doppler_shift(data, rtt, sample_rate)

    # Construct the filename using an f-string
    filename = (
        f"vdif_sr{sample_rate / 1e6:.1f}MHz_bw{bandwidth / 1e6:.1f}MHz_"
        f"pw{pulse_width * 1e6:.1f}us_pp{pulse_period * 1e6:.1f}us_"
        f"dur{duration:.1f}s_epoch{epoch:.0f}_"
        f"start{seconds_since_epoch:.0f}s_snr{SNR}_"
        f"{'randomPhase' if randomise_phase else 'fixedPhase'}_"
        f"{'dopplerShift' if add_doppler_shift else 'noDoppler'}.vdif"
    )

    print(f"VDIF file will be saved as: {filename}")

    create_vdif_file(
        data_array=data,
        sample_rate=sample_rate,
        filename=filename,
        start_seconds_from_epoch=seconds_since_epoch,
        epoch=epoch,
        bits_per_sample=bits_per_sample
    )

    print("Done")

def plots_to_pdf(directory='plots', output_pdf='compiled_images.pdf'):
    """
    Finds all PNG images in a directory, compiles them into a single PDF, and deletes the original PNGs.

    Parameters:
    - directory (str): Folder to search for PNG images. Defaults to current directory.
    - output_pdf (str): Name of the output PDF file.

    Returns:
    - str: The path to the generated PDF file.
    """
    # Find all PNG files in the directory
    png_files = [f for f in os.listdir(directory) if f.lower().endswith('.png')]
    png_files.sort()  # Optional: Sort files alphabetically

    if not png_files:
        print("No PNG files found in the directory.")
        return None

    # Open the first image
    first_image_path = os.path.join(directory, png_files[0])
    first_image = Image.open(first_image_path).convert('RGB')

    # Open the rest of the images
    image_list = []
    for file in png_files[1:]:
        img_path = os.path.join(directory, file)
        img = Image.open(img_path).convert('RGB')
        image_list.append(img)

    # Save all images to a single PDF
    output_path = os.path.join(directory, output_pdf)
    first_image.save(output_path, save_all=True, append_images=image_list)

    print(f"PDF saved as {output_path}")

    # Delete the original PNG files after successful PDF creation
    try:
        for file in png_files:
            os.remove(os.path.join(directory, file))
        print("Original PNG files deleted successfully.")
    except Exception as e:
        print(f"Error deleting PNG files: {e}")

    return output_path

# Example usage
if __name__ == "__main__":
    # Parameters
    sample_rate = int(8e6)  # 8 MHz
    B = 4e6  # Bandwidth
    chirp_length = 2.5e-6  # Chirp duration
    signal_period = 25e-6  # Time between chirps
    duration_seconds = 0.001  # Total duration of the signal
    start_seconds_from_epoch = 15572400 # Example GPS time
    station_id = 1234  # Example station ID
    bits_per_sample = 8  # Bits per sample
    epoch = 48

    # Dictionary of SNR ratios and randomise_phase flags
    snr_dict = [
        # (0.05, False),
        # (0.06, True),
        # (0.1, False),
        # (0.15, True),
        # (0.2, False),
        # (0.2, True),
        # (0.3, False),
        # (0.3, True),
        # (0.5, False),
        # (0.7, True),
        # (1.0, False),
        # (1.0, True),
        # (5.0, False),
        # (5.0, True),  
        # (10.0, False),
        (100000.0, False),        
        # (30.0, False),
        # (30.0, True),
    ]

    # Loop through the dictionary and generate VDIF files
    for SNR, randomise_phase in snr_dict:
        signal_portion = SNR / (SNR + 1)
        noise_portion = 1 / (SNR + 1)

        # Generate FM chirp signal
        data = generate_fm_chirp(B, chirp_length, signal_period, sample_rate, duration_seconds, signal_portion, randomise_phase)
        data = add_noise(data, noise_portion)

        # print(len(data))

        filename = f"presentation_LFM_B_{B}_SNR_{SNR}_pulseT_{signal_period}_pulseW_{chirp_length}_phaseRand_{randomise_phase}.vdif"
        create_vdif_file(
            data_array=data,
            sample_rate=sample_rate,
            filename=filename,
            start_seconds_from_epoch=start_seconds_from_epoch,
            epoch=epoch,
            station_id=station_id,
            bits_per_sample=bits_per_sample
        )