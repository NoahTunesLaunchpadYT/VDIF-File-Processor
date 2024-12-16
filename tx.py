import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import chirp
from scipy.signal import correlate

# Parameters
total_duration = 0.01  # Total duration in seconds
sampling_frequency = 8e6  # Sampling frequency in Hz
chirp_duration = 2.5e-6  # Chirp duration in seconds
chirp_start_freq = 0  # Chirp start frequency in Hz
chirp_end_freq = 4e6  # Chirp end frequency in Hz
repeat_interval = 25e-6  # Interval between chirps in seconds

# Derived parameters
samples_per_chirp = int(chirp_duration * sampling_frequency)
samples_per_kernal = samples_per_chirp * 3000
samples_per_interval = int(repeat_interval * sampling_frequency)
total_samples = int(total_duration * sampling_frequency)

# Time vector for a single chirp
t_chirp = np.linspace(0, chirp_duration, samples_per_chirp, endpoint=False)

# Generate the chirp signal
chirp_signal = chirp(t_chirp, f0=chirp_start_freq, f1=chirp_end_freq, t1=chirp_duration, method='linear')

# Scale the chirp signal to the range [-1, 1] for signed 8-bit integers, then divide by 8
chirp_signal_scaled = (chirp_signal * 127).astype(np.int8)

# Create the full signal array with silence intervals
signal = np.zeros(total_samples, dtype=np.int8)
for i in range(0, total_samples, samples_per_interval):
    end_idx = i + samples_per_chirp
    if end_idx > total_samples:
        break
    signal[i:end_idx] = chirp_signal_scaled

chirp_10 = signal[8030:8030+samples_per_kernal]

# Generate analogue noise with the same amplitude range as 8-bit signed integers
noise = np.random.uniform(-127, 127, total_samples).astype(np.int8)

# Add noise to the signal
signal_with_noise = signal * 0.01 + noise * 0.99

# Cross-correlate the signal with the original chirp signal
correlation = correlate(signal_with_noise, chirp_10)

# Perform Fourier Transform on the correlation result
correlation_fft = np.fft.fft(correlation)
frequencies = np.fft.fftfreq(len(correlation), 1 / sampling_frequency)

# Compute the magnitude of the FFT (frequency spectrum)
magnitude = np.abs(correlation_fft)
phase = np.angle(correlation_fft)

# Time vectors for plotting
time_signal = np.linspace(0, total_duration, total_samples, endpoint=False)
time_correlation = np.linspace(0, total_duration, len(correlation), endpoint=False)
time_fft = np.fft.fftfreq(len(correlation), 1 / sampling_frequency)

# Plotting the original signal, noisy signal, and chirp signal in a single window
fig, (ax_orig, ax_noise, ax_chirp, ax_corr) = plt.subplots(4, 1, sharex=True)
ax_orig.plot(time_signal, signal)
ax_orig.set_title("Original Signal")

ax_noise.plot(time_signal, signal_with_noise)
ax_noise.set_title("Signal with Noise")

ax_chirp.plot(time_signal[:samples_per_kernal], chirp_10)
ax_chirp.set_title("'Chirp'Kernal")

ax_corr.plot(time_correlation, correlation)
ax_corr.set_title("Correlation with Chirp")

fig.tight_layout()
plt.show(block=False)  # Use block=False to avoid blocking execution

# Plotting the FFT in a new window
fig_fft = plt.figure()
ax_fft = fig_fft.add_subplot(111)
ax_fft.plot(time_fft[:len(time_fft)//2], magnitude[:len(magnitude)//2])  # Only plot the positive frequencies
ax_fft.set_title("FFT of Correlation")
ax_fft.set_xlabel("Frequency (Hz)")
ax_fft.set_ylabel("Magnitude")

fig_fft.tight_layout()
plt.show(block=False)  # Use block=False to avoid blocking execution

# Plotting the FFT in a new window
fig_fft = plt.figure()
ax_fft = fig_fft.add_subplot(111)
ax_fft.plot(time_fft[:len(time_fft)//2], phase[:len(magnitude)//2])  # Only plot the positive frequencies
ax_fft.set_title("FFT of Correlation")
ax_fft.set_xlabel("Frequency (Hz)")
ax_fft.set_ylabel("Angle")

fig_fft.tight_layout()
plt.show()  # Use block=False to avoid blocking execution
