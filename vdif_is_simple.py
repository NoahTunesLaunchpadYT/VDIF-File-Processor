import os
import mmap
from tqdm import tqdm
from collections import defaultdict
import vdif_datetime as dt
import vdif_data_frame_reader as fr

def check_simplicity(file_path):
    """
    Processes a VDIF file to extract properties and determine if it is "simple,"
    "contiguous," and "ordered."
    
    A "simple" VDIF file has the same number of frames associated with each second.
    A "contiguous" VDIF file has each elapsed second incrementing by one.
    An "ordered" VDIF file has time stamps in ascending order.
    
    Args:
        file_path (str): Path to the VDIF file.
    """
    try:
        file_size = os.path.getsize(file_path)  # Get the total file size for progress tracking

        with open(file_path, 'rb') as file:
            # Memory-map the file for efficient access
            mmapped_file = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)

            total_frames = 0
            total_samples = 0
            reference_epoch = None
            start_seconds_from_epoch = None
            end_seconds_from_epoch = None
            frames_per_second = defaultdict(int)  # Count frames per second

            previous_second = None
            is_contiguous = True
            is_ordered = True

            with tqdm(total=file_size, unit='B', unit_scale=True, desc="Processing VDIF") as pbar:
                offset = 0

                while offset < file_size:
                    # Read the header of the current frame from the memory-mapped file
                    header_info = fr.read_vdif_frame_header_fast(mmapped_file, offset)

                    if reference_epoch is None:
                        # Set reference epoch and starting time
                        reference_epoch = header_info['reference_epoch']
                        start_seconds_from_epoch = header_info['seconds_from_epoch']

                    # Update the ending time as the file is read
                    current_second = header_info['seconds_from_epoch']
                    if previous_second is not None:
                        # Check if seconds are contiguous
                        if current_second != previous_second + 1 and current_second != previous_second:
                            is_contiguous = False
                        # Check if seconds are ordered
                        if current_second < previous_second:
                            is_ordered = False

                    previous_second = current_second
                    end_seconds_from_epoch = current_second
                    
                    # Count frames for the current second
                    frames_per_second[current_second] += 1
                    
                    # Increment frame and sample counters
                    total_frames += 1
                    total_samples += header_info['num_channels'] * header_info['frame_length']

                    # Calculate frame length and update the offset
                    frame_length = header_info['frame_length']
                    offset += frame_length

                    # Update progress bar
                    pbar.update(frame_length)

            # Check if the file is "simple"
            frame_counts = set(frames_per_second.values())
            is_simple = len(frame_counts) == 1  # Simple if all seconds have the same frame count
    except Exception as e:
        print(f"Error while processing VDIF file: {e}")
        return

    # Convert seconds to human-readable date and time
    start_datetime = dt.convert_to_datetime(reference_epoch, start_seconds_from_epoch)
    end_datetime = dt.convert_to_datetime(reference_epoch, end_seconds_from_epoch + 1)

    # Print file properties and simplicity checks
    print("")
    print("=" * 40)
    print("VDIF File Properties & Simplicity")
    print("=" * 40)
    print(f"Start Date and Time: {start_datetime}")
    print(f"End Date and Time: {end_datetime}")
    print(f"Total Number of Frames: {total_frames}")
    print(f"Total Number of Samples: {total_samples}")
    print(f"Reference Epoch: {reference_epoch}")
    print(f"File Simplicity: {'Simple' if is_simple else 'Not Simple'}")
    print(f"File Contiguity: {'Contiguous' if is_contiguous else 'Not Contiguous'}")
    print(f"File Order: {'Ordered' if is_ordered else 'Not Ordered'}")
    
    if not is_simple:
        print("\nFrame counts per second:")
        for second, count in frames_per_second.items():
            print(f"Second {second}: {count} frames")
    print("")
