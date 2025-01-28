import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def plot_auto_correlation(data, resolution, file_path, pdf_file="auto_correlation_plots.pdf"):
    """
    Perform match filtering on the input data and generate plots.

    Args:
        data (np.ndarray): The input signal with time in the first column and voltage data in the second column.
        resolution (float): Sampling resolution (samples per second).
        file_path (str): Path to the input file for the subtitle.
        pdf_file (str): Name of the output PDF file to save the plots.
    """
    # Create a figure with 2x2 subplots, sharing the x-axis for the first column
    fig, axs = plt.subplots(2, 2, figsize=(12, 10), sharex='col')

    # Add a main title
    fig.suptitle("Match Filtering Results", fontsize=16, y=1.0)

    # Add a subtitle using fig.text
    fig.text(0.5, 0.97, f"File: {file_path}", fontsize=12, ha='center', va='top', style='italic')

    print("Plotting voltage data...")

    # Plot the original signal (top left)
    t = data[:, 0]
    input_data = data[:, 1]
    axs[0, 0].plot(input_data, label="$s_C (τ)$")
    axs[0, 0].set_title("Original Signal, $s_C (τ)$")
    axs[0, 0].set_xlabel("Time (s)")
    axs[0, 0].set_ylabel("Amplitude (V)")
    axs[0, 0].legend(loc="upper right")
    axs[0, 0].grid(True)

    print("Plotting FFT...")

    # Compute the FFT of the input data (top right)
    fft_result = np.fft.fft(input_data)
    frequency = np.fft.fftfreq(len(input_data), d=1/resolution)
    positive_frequencies = frequency[:len(frequency)//2]
    positive_fft = fft_result[:len(frequency)//2]

    axs[0, 1].plot(positive_frequencies, np.abs(positive_fft), label="$S_C(f) = F[s_C(τ)]$")
    axs[0, 1].set_title("FFT of Input Signal, $S_C(f)$")
    axs[0, 1].set_xlabel("Frequency (Hz)")
    axs[0, 1].set_ylabel("Amplitude (V)")
    axs[0, 1].legend(loc="upper right")
    axs[0, 1].grid(True)

    print("Plotting Power Spectrum...")

    # Compute the power spectrum (bottom right)
    power_spectrum = fft_result * np.conjugate(fft_result)
    positive_power_spectrum = power_spectrum[:len(frequency)//2]

    axs[1, 1].plot(positive_frequencies, np.abs(positive_power_spectrum), label="$C_S (f) = S_C(f) S_C^{*} (f)$")
    axs[1, 1].set_title("Power Spectrum, $C_S (f)$")
    axs[1, 1].set_xlabel("Frequency (Hz)")
    axs[1, 1].set_ylabel("Power $|V|^2$")
    axs[1, 1].legend(loc="upper right")
    axs[1, 1].grid(True)

    print("Plotting Correlation...")

    # Compute the inverse FFT of the power spectrum (bottom left)
    ifft_result = np.fft.ifft(power_spectrum).real
    for i in range(100):
        ifft_result[i] = 0  # Set the 0-shift spike to 0
        ifft_result[-i] = 0  # Set the 0-shift spike to 0

    axs[1, 0].plot(ifft_result**2, label="$c_S(t)^2 = F^{-1}[C_S (f)] ^2$", alpha=0.8)
    axs[1, 0].set_title("Match Filtered Signal, $c_S(t)^2$")
    axs[1, 0].set_xlabel("Time (s)")
    axs[1, 0].set_ylabel("Power $|V|^2$")
    axs[1, 0].legend(loc="upper right")
    axs[1, 0].grid(True)

    print("Creating Fast Time vs. Slow Time Plot...")

    ifft_result = ifft_result[100:]

    # Reshape the data for fast time vs. slow time plot
    fast_time_duration = 25e-6  # 25 microseconds
    slow_time_duration = len(ifft_result)/resolution

    # Calculate the number of samples in fast time and slow time
    fast_time_samples = int(fast_time_duration * resolution)
    slow_time_samples = int(slow_time_duration / fast_time_duration)

    # Reshape the ifft_result into a 2D grid
    correlation_2d = ifft_result[:fast_time_samples * slow_time_samples].reshape(slow_time_samples, fast_time_samples)

    # Create a new figure for the Fast Time vs. Slow Time plot
    fig2, (ax2, ax3) = plt.subplots(2, 1, figsize=(10, 10), gridspec_kw={'height_ratios': [3, 1]})

    # Plot the 2D correlation as a heatmap
    im = ax2.imshow(np.abs(correlation_2d), aspect='auto', cmap='viridis', 
                    extent=[-fast_time_duration * 1e6/2, fast_time_duration * 1e6/2, slow_time_duration, 0])  # Convert fast time to microseconds
    ax2.set_xlabel("Fast Time (µs)")
    ax2.set_ylabel("Slow Time (s)")
    ax2.set_title("Fast Time vs. Slow Time Correlation")

    # Calculate and plot the intensity line below the heatmap
    intensity = np.sum(np.abs(correlation_2d), axis=0)  # Sum down the columns
    fast_time_axis = np.linspace(-fast_time_duration * 1e6/2, fast_time_duration * 1e6/2, fast_time_samples)

    ax3.plot(fast_time_axis, intensity, label="Intensity vs. Fast Time")
    ax3.set_xlabel("Fast Time (µs)")
    ax3.set_ylabel("Intensity")
    ax3.set_title("Summed Intensity Across Slow Time")
    ax3.legend(loc="upper right")
    ax3.grid(True)

    # Adjust layout to ensure no overlap
    fig2.tight_layout(rect=[0, 0, 0.85, 1])  # Leave space for the color bar

    # Add colorbar manually outside the main plot
    cbar_ax = fig2.add_axes([0.88, 0.15, 0.02, 0.7])  # Position of the color bar
    fig2.colorbar(im, cax=cbar_ax, label="Magnitude")

    print("Showing plots...")
    # Show the plots
    plt.show()

    print(f"Saving to '{pdf_file}'...")
    # Save the plots to a PDF
    with PdfPages(pdf_file) as pdf:
        pdf.savefig(fig)
        pdf.savefig(fig2)
    plt.close(fig)
    plt.close(fig2)
    print("Done")
