import vdif_properties as props
import mmap
import vdif_data_frame_reader as fr
import vdif_datetime as dt

def process_data_window(file_path, process_function):
    """
    Process a VDIF file by extracting data for a user-specified time range and applying a function.
    Args:
        file_path (str): Path to the VDIF file.
        process_function (callable): Function to process the extracted data (e.g., plotting or printing).
    """
    file_info = props.print_vdif_file_properties(file_path)
    start_seconds, end_seconds = dt.get_time_range_from_user(file_info)

    with open(file_path, 'rb') as file:
        mmapped_file = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)
        starting_header, data = fr.generate_data_from_time_range(file_info, mmapped_file, start_seconds, end_seconds)

    process_function(file_info, starting_header, data, start_seconds, end_seconds)

