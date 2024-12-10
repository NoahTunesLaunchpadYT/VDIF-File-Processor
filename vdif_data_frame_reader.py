"""
-------------------------------------------------
File: vdif_data_frame_reader.py
Author: Noah West
Date: 6/12/2024
Description: Reads one dataframe of a vdif file
License: see LICENCE.txt
Dependencies:
    - struct
    - numpy
    - matplotlib
-------------------------------------------------
"""

import struct
import numpy as np

# For unpacking an arbitrary range of frames
def generate_data_from_time_range(file_info, 
                                  mmapped_file, 
                                  start_seconds_from_epoch, 
                                  end_seconds_from_epoch):
    """
    Generates the data from the VDIF frames between the specified time range.
    Args:
        file_info (dict): Information about the VDIF file.
        mmapped_file (mmap.mmap): Memory-mapped file object.
        start_seconds (float): The start time in seconds since the VDIF file's reference epoch.
        end_seconds (float): The end time in seconds since the VDIF file's reference epoch.
    Returns:
        np.ndarray: The continuous data array, including time and value.
    """
    # Extract the frame length and frames per second from the file info
    frame_length = file_info["frame_length"]
    frames_per_second = file_info["frames_per_second"]
    file_seconds_from_epoch = file_info["start_seconds_from_epoch"]

    # Calculate time relative to the start of the file
    start_seconds = start_seconds_from_epoch - file_seconds_from_epoch
    end_seconds = end_seconds_from_epoch - file_seconds_from_epoch

    # Calculate the byte offset for the start and end times
    start_offset = int(frames_per_second * start_seconds) * frame_length
    end_offset = int(frames_per_second * end_seconds) * frame_length

    # Initialize a numpy array to store the continuous data
    all_data = []

    # Start at the beginning of the selected range
    offset = start_offset
    starting_header_info = None

    while offset < end_offset:
        # Read each frame's header and data
        if starting_header_info == None:
            starting_header_info, data = read_vdif_frame_data(mmapped_file, offset, file_info)
        else:
            temp, data = read_vdif_frame_data(mmapped_file, offset, file_info)

        # Append data to the continuous array
        all_data.append(data)

        # Move to the next frame
        offset += frame_length

    # Convert the list of data arrays into a single continuous numpy array
    all_data = np.vstack(all_data)

    return starting_header_info, all_data

def unpack_vdif_header_start(header_bytes):
    """
    Unpacks and interprets first half of a VDIF Data Frame Header.
    Args:
        header_bytes (bytes): The first 16 bytes of the header.
    Returns:
        dict: Parsed header fields.
    """
    if len(header_bytes) < 16:
        raise ValueError("Header is too short. Expected at least 16 bytes.")

    # Unpack Words 0-3
    word_0, word_1, word_2, word_3 = struct.unpack('<IIII', header_bytes[:16])

    # Parse fields from Word 0
    invalid_data = (word_0 >> 31) & 0x1
    legacy_mode = (word_0 >> 30) & 0x1
    seconds_from_epoch = word_0 & 0x3FFFFFFF

    # Parse fields from Word 1
    reference_epoch = (word_1 >> 24) & 0x3F
    frame_number = word_1 & 0xFFFFFF

    # Parse fields from Word 2
    vdif_version = (word_2 >> 29) & 0x7
    log2_channels = (word_2 >> 24) & 0x1F
    num_channels = 2 ** log2_channels
    frame_length = word_2 & 0xFFFFFF

    # Parse fields from Word 3
    data_type = (word_3 >> 31) & 0x1
    bits_per_sample = ((word_3 >> 26) & 0x1F) + 1
    thread_id = (word_3 >> 16) & 0x3FF
    station_id = word_3 & 0xFFFF

    return {
        "invalid_data": invalid_data,
        "legacy_mode": legacy_mode,
        "seconds_from_epoch": seconds_from_epoch,
        "reference_epoch": reference_epoch,
        "frame_number": frame_number,
        "vdif_version": vdif_version,
        "num_channels": num_channels,
        "frame_length": frame_length * 8,  # Convert 8-byte units to bytes
        "data_type": "Complex" if data_type else "Real",
        "bits_per_sample": bits_per_sample,
        "thread_id": thread_id,
        "station_id": station_id,
    }

def unpack_vdif_extended_user_data(header_bytes):
    extended_data = header_bytes  # Words 4-7

    return {
        "extended_data": extended_data.hex()
    }

def read_vdif_frame_data(mmapped_file, offset, file_info):
    """
    Reads a VDIF frame from an mmapped file starting at a given offset.

    Args:
        mmapped_file: Memory-mapped file object containing the VDIF data.
        offset (int): The offset in the file where the VDIF frame starts.
        file_info (dict): File metadata containing 'frames_per_second'.

    Returns:
        tuple: 
            - header_info (dict): Parsed header information from the VDIF frame.
            - np.array: The unpacked data samples as a 2D array with columns [time, value].
    """
    # Read header information from the specified offset
    header_info = read_vdif_frame_header(mmapped_file, offset)

    # Extract frame length, bits per sample, and other header details
    frame_length = header_info["frame_length"]
    bits_per_sample = header_info["bits_per_sample"]
    seconds_from_epoch = header_info["seconds_from_epoch"]
    frame_number = header_info["frame_number"]
    frames_per_second = file_info["frames_per_second"]

    # Calculate header size and data length
    header_size = 32 if header_info["legacy_mode"] == 0 else 16

    # Read the data portion of the frame
    data_bytes = mmapped_file[offset + header_size: offset + frame_length]

    # Unpack data based on bits per sample
    if bits_per_sample == 8:
        data = np.frombuffer(data_bytes, dtype=np.uint8)
    elif bits_per_sample == 16:
        data = np.frombuffer(data_bytes, dtype=np.int16)
    else:
        raise ValueError(f"Unsupported bits per sample: {bits_per_sample}")
    
    # Adjust data values
    data = data - 2**(bits_per_sample - 1)
    data = data.astype(np.int8)

    # Generate time data for each sample
    time_base = seconds_from_epoch + frame_number / frames_per_second
    time_data = np.array([time_base + i / (len(data) * frames_per_second) for i in range(len(data))])

    # Combine time and value data into a 2D array
    result = np.column_stack((time_data, data))

    return header_info, result

def read_vdif_frame_header(mmapped_file, offset):
    """
    Reads the VDIF frame header from a memory-mapped file at the specified offset.
    
    Args:
        mmapped_file: Memory-mapped file object.
        offset (int): Offset in the file where the VDIF frame starts.
    
    Returns:
        dict: Parsed VDIF header fields.
    """
    # Read the first 16 bytes of the VDIF header
    header_bytes = mmapped_file[offset : offset + 16]
    header_info1 = unpack_vdif_header_start(header_bytes)

    header_info2 = {}
    if not header_info1["legacy_mode"]:
        # Read the next 16 bytes for extended user data
        extended_bytes = mmapped_file[offset + 16 : offset + 32]
        header_info2 = unpack_vdif_extended_user_data(extended_bytes)

    # Merge basic and extended header information
    header_info = header_info1 | header_info2

    return header_info

