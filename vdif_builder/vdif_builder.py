import numpy as np
import struct

def create_vdif_file(data_array, sample_rate, filename, 
                    start_seconds_from_epoch=0.0, station_id=0,
                    bits_per_sample=8):
    """
    Creates a single-channel VDIF file from a numpy array.
    
    Args:
        data_array (np.ndarray): Input data array (int8 or int16)
        sample_rate (int): Samples per second (e.g., 8e6)
        filename (str): Output filename
        start_seconds_from_epoch (float): Start time in seconds since reference epoch
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
    num_frames = len(data_array) // samples_per_frame
    # print(f"samples per frame: {samples_per_frame}")
    # print(num_frames)
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
                (0 << 24) | (frame_number & 0xFFFFFF),  # Reference epoch = 0
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

def generate_test_signal(sample_rate, duration_seconds, freq=1000):
    """
    Generates a test signal for demonstration.
    
    Args:
        sample_rate (int): Samples per second
        duration_seconds (float): Signal duration in seconds
        freq (int): Frequency of test tone in Hz
    
    Returns:
        np.ndarray: int16 array of generated signal
    """
    t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds))
    signal = np.sin(2 * np.pi * freq * t)
    return (signal * 127).astype(np.int8)

def generate_fm_chirp(B, chirp_length, signal_period, sample_rate, total_duration, signal_portion, randomise_phase=False):
    """
    Generate an FM chirp signal with specified parameters, preallocating the array.
    
    Args:
        B (float): Bandwidth (Hz).
        chirp_length (float): Duration of one chirp (seconds).
        signal_period (float): Time between chirps (seconds).
        sample_rate (float): Sampling rate (samples/second).
        total_duration (float): Total duration of the signal (seconds).
        randomise_phase (bool): Randomize phase for each chirp (default: False).
    
    Returns:
        np.ndarray: Generated signal (complex-valued).
    """
    # Calculate total samples and preallocate array
    total_samples = int(total_duration * sample_rate)
    signal = np.zeros(total_samples, dtype=np.complex128)
    
    # Time vector for one chirp
    t_chirp = np.linspace(0, chirp_length, int(chirp_length * sample_rate), endpoint=False)
    chirp_samples = len(t_chirp)
    
    current_sample = 0  # Track the current sample index
    
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
        else:
            break  # Exit loop if no space for another chirp
    
    return (signal*63*signal_portion).astype(np.int8)

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

# Example usage
if __name__ == "__main__":
    # Parameters
    sample_rate = int(8e6)  # 8 MHz
    B = 4e6  # Bandwidth
    chirp_length = 2.5e-6  # Chirp duration
    signal_period = 25e-6  # Time between chirps
    duration_seconds = 10  # Total duration of the signal
    start_seconds_from_epoch = 123456789.000  # Example GPS time
    station_id = 1234  # Example station ID
    bits_per_sample = 8  # Bits per sample

    # Dictionary of SNR ratios and randomise_phase flags
    snr_dict = [
        (0.05, False),
        (0.05, True),
        (0.1, False),
        (0.1, True),
        (0.5, False),
        (0.5, True),
        (1.0, False),
        (1.0, True),
        (5.0, False),
        (5.0, True),  
        (10.0, False),
        (10.0, True),        
        (30.0, False),
        (30.0, True),
    ]

    # Loop through the dictionary and generate VDIF files
    for SNR, randomise_phase in snr_dict:
        signal_portion = SNR / (SNR + 1)
        noise_portion = 1 / (SNR + 1)

        # Generate FM chirp signal
        data = generate_fm_chirp(B, chirp_length, signal_period, sample_rate, duration_seconds, signal_portion, randomise_phase)
        data = add_noise(data, noise_portion)

        # print(len(data))

        filename = f"synthetic_LFM_B_{B}_SNR_{SNR}_pulseT_{signal_period}_pulseW_{chirp_length}_phaseRand_{randomise_phase}.vdif"
        create_vdif_file(
            data_array=data,
            sample_rate=sample_rate,
            filename=filename,
            start_seconds_from_epoch=start_seconds_from_epoch,
            station_id=station_id,
            bits_per_sample=bits_per_sample
        )