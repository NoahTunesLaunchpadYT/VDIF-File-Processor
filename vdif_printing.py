import vdif_data_frame_reader as fr
import vdif_datetime as dt
import vdif_properties as props
import mmap

# PUBLIC FUNCTIONS

def print_first_frame_short(file_path):
    read_and_print_frame(file_path)

def print_first_frame_all(file_path):
    read_and_print_frame(file_path, print_all=True)

def print_frames(file_path):
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
        starting_header, data = fr.generate_data_from_time_range(file_info, mmapped_file, start_seconds, end_seconds)

        # Print details about the retrieved data
        start_datetime = dt.convert_to_datetime(file_info["reference_epoch"], start_seconds)
        end_datetime = dt.convert_to_datetime(file_info["reference_epoch"], end_seconds)

        # Visualize the start and end of the data
        print_header(starting_header)
        print_data(data)        
        print(f"Data range from {start_seconds} to {end_seconds} seconds since epoch")
        print(f"Data range from {start_datetime} to {end_datetime} since epoch")
        print(f"Number of samples: {len(data)}")
        print("")



#HELPER FUNCTIONS

def read_and_print_frame(file_path, print_all=False, offset=0):
    file_info = props.get_vdif_file_properties(file_path)

    # Memory-map the file for efficient access
    with open(file_path, 'rb') as file:
        mmapped_file = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)
        # Read the first frame's header and data
        header_info, data = fr.read_vdif_frame_data(mmapped_file, offset, file_info)
    
    # Print frame header
    print_header(header_info)
    
    # Print frame data
    if print_all:
        print_data(data, len(data), 0)
    else:
        print_data(data)

def print_header(header_info):
    # PRINTING HEADER
    print("\n\n\n" + "=" * 36)
    print("      VDIF Header Information")
    print("=" * 36)

    for key, value in header_info.items():
        print(f"  {key:<20}|\t{value}")
    
def print_data(data, start_rows=5, end_rows=5):
    # PRINTING DATA
    print("\n\n" + "=" * 36)
    print("            VDIF Data")
    print("=" * 36)

    print(f"  {"Time since epoch (s)":<19} | {"Amplitude":<10}\n")


    # Print the first 5 and last 5 rows with right alignment
    for i in range(0, start_rows):
        print(f"  {data[i][0]:<20.8f} | {int(data[i][1]):>10}")

    if end_rows:
        print("...")

        for i in range(len(data) - (end_rows + 1), len(data) - 1):
            print(f"  {data[i][0]:<20.8f} | {int(data[i][1]):>10}")

    print("(End of data)\n")