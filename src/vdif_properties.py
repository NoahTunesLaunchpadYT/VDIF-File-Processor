import os
import mmap
import src.vdif_data_frame_reader as fr
import src.vdif_datetime as dt

def get_vdif_file_properties(file_path):
    """
    Reads the first and last frames of a VDIF file to compute essential properties, including the sampling rate.
    
    Args:
        file_path (str): Path to the VDIF file.
        
    Returns:
        dict: A dictionary containing the computed properties of the VDIF file.
    """
    try:
        file_size = os.path.getsize(file_path)  # Get the total file size

        with open(file_path, 'rb') as file:
            # Memory-map the file for efficient access
            mmapped_file = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)

            # Read the first frame
            offset = 0
            header_info = fr.read_vdif_frame_header(mmapped_file, offset)
            header_size = 32 if header_info["legacy_mode"] == 0 else 16
            frame_length = header_info["frame_length"]
            bytes_per_sample = header_info["bits_per_sample"] / 8
            samples_per_frame = (frame_length - header_size) / bytes_per_sample
            reference_epoch = header_info["reference_epoch"]
            start_seconds_from_epoch = header_info["seconds_from_epoch"]

            # Jump to the last frame
            last_frame_offset = file_size - frame_length
            last_frame_header = fr.read_vdif_frame_header(mmapped_file, last_frame_offset)
            end_seconds_from_epoch = last_frame_header["seconds_from_epoch"] + 1
            frame_number_of_last_frame = last_frame_header["frame_number"]

            # Calculate derived properties
            total_frames = file_size // frame_length
            total_samples = total_frames * samples_per_frame
            frames_per_second = frame_number_of_last_frame + 1

            # Calculate sampling rate
            sampling_rate = frames_per_second * samples_per_frame

            # Convert seconds to human-readable date and time
            start_datetime = dt.convert_to_datetime(reference_epoch, start_seconds_from_epoch)
            end_datetime = dt.convert_to_datetime(reference_epoch, end_seconds_from_epoch + 1)

            # Return properties as a dictionary
            return {
                "start_datetime": start_datetime,
                "end_datetime": end_datetime,
                "frame_length": frame_length,
                "total_frames": total_frames,
                "total_samples": int(total_samples),
                "reference_epoch": reference_epoch,
                "frames_per_second": frames_per_second,
                "samples_per_frame": samples_per_frame,
                "sample_rate": sampling_rate,
                "start_seconds_from_epoch": start_seconds_from_epoch,
                "end_seconds_from_epoch": end_seconds_from_epoch,
            }
    except Exception as e:
        print(f"Error while processing VDIF file: {e}")
        return None


def print_vdif_file_properties(file_path):
    """
    Prints the properties of a VDIF file.
    
    Args:
        file_properties (dict): A dictionary containing the VDIF file properties.
    """
    file_properties = get_vdif_file_properties(file_path)

    print("\n" + "=" * 40)
    print("VDIF File Properties")
    print("=" * 40)
    print(f"Start Date and Time: {file_properties['start_datetime']}")
    print(f"End Date and Time: {file_properties['end_datetime']}")
    print(f"Total Number of Frames: {file_properties['total_frames']}")
    print(f"Total Number of Samples: {file_properties['total_samples']}")
    print(f"Reference Epoch: {file_properties['reference_epoch']}")
    print(f"Frames Per Second: {file_properties['frames_per_second']}")
    print(f"Sample rate: {file_properties['sample_rate']} Hz")
    print(f"Seconds Since Epoch of Start of File: {file_properties['start_seconds_from_epoch']}")
    print(f"Seconds Since Epoch of End of File: {file_properties['end_seconds_from_epoch']}")
    print("")

    return file_properties
