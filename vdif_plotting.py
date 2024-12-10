import vdif_data_frame_reader as fr
import vdif_properties as props
import vdif_datetime as dt
import matplotlib.pyplot as plt
import mmap

def plot_first_frame(file_path):
    with open(file_path, 'rb') as file:
        # Read and plot the first frame of data
        header_info, data = fr.read_vdif_frame_data(file)
        
        plot_data(data)

def plot_data(data):
    plt.figure(figsize=(10, 5))
    plt.plot(data[:,0], data[:,1], label="Data Samples")
    plt.title("VDIF Frame Data")
    plt.xlabel("Time since epoch")
    plt.ylabel("Amplitude")
    plt.legend(loc="upper right")
    plt.grid()
    plt.show()


def plot_frames(file_path):
    """
    Prints a range of frames from the VDIF file based on the user input time range.
    Args:
        file_path (str): The path to the VDIF file.
    """
    file_info = props.print_vdif_file_properties(file_path)

    # Get the time range from the user since epoch
    start_seconds, end_seconds = dt.get_time_range_from_user(file_info)

    # Open the VDIF file and memory-map it for efficient access
    with open(file_path, 'rb') as file:
        mmapped_file = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)

        # Generate the data over the time period
        print("\nGenerating data...")
        temp, data = fr.generate_data_from_time_range(file_info, mmapped_file, start_seconds, end_seconds)

        # Visualize the start and end of the data
        print("Plotting data...")
        plot_data(data)
        print("Plot closed \n")


