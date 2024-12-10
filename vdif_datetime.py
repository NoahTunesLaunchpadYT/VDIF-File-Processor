from datetime import datetime, timedelta

from datetime import datetime, timedelta

def convert_to_datetime(reference_epoch, seconds_from_epoch):
    """
    Converts reference epoch and seconds from epoch to a human-readable datetime with milliseconds.
    
    Args:
        reference_epoch (int): The reference epoch as a 6-bit value.
        seconds_from_epoch (float): Seconds since the reference epoch, including fractions for milliseconds.
    
    Returns:
        str: Human-readable date and time with milliseconds.
    """
    # Base date: 00:00 UTC, 1 Jan 2000
    base_year = 2000
    base_month = 1
    months_offset = reference_epoch % 64

    # Calculate actual year and month
    year = base_year + (months_offset // 2)
    month = base_month + (months_offset % 2) * 6

    # Compute datetime
    base_datetime = datetime(year, month, 1)
    
    # Calculate seconds and milliseconds from the input
    seconds = int(seconds_from_epoch)
    milliseconds = int((seconds_from_epoch - seconds) * 1000)

    # Create final datetime object
    final_datetime = base_datetime + timedelta(seconds=seconds)
    
    # Add milliseconds manually
    final_datetime_with_ms = final_datetime.replace(microsecond=milliseconds * 1000)

    # Format the datetime with milliseconds
    return final_datetime_with_ms.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # Remove last three digits for milliseconds

def parse_time_input(time_str, file_info):
    """
    Parses the user input time string into seconds since the VDIF file's reference epoch.
    Args:
        time_str (str): The time string input by the user (either in datetime or seconds since epoch format).
        file_info (dict): Information about the VDIF file, including the reference epoch (in half-years since 2000).
    Returns:
        float: The time in seconds since the VDIF file's reference epoch.
    """
    try:
        # Try to parse as seconds since epoch (float)
        seconds_since_epoch = float(time_str)
        return seconds_since_epoch
    except ValueError:
        # If it's not a valid float, assume it's in datetime format
        try:
            parsed_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            raise ValueError("Invalid time format. Please use datetime format (YYYY-MM-DD HH:MM:SS.sss) or seconds since epoch.")

    # Get the reference epoch from file_info (in half-years since 2000)
    reference_epoch = file_info["reference_epoch"]

    # Calculate the reference datetime (January 1st, 2000, 00:00:00)
    epoch_start = datetime(2000, 1, 1)

    # Calculate the start of the month (epoch_time) from the reference epoch
    # Calculate the month and year from the reference epoch
    half_years = reference_epoch  # The number of half years since 2000
    start_year = 2000 + (half_years // 2)
    start_month = 1 if half_years % 2 == 0 else 7

    # Create the start of the month (epoch_time) datetime
    epoch_time = datetime(start_year, start_month, 1)

    # Calculate seconds since epoch
    seconds_since_epoch = (parsed_time - epoch_time).total_seconds()

    return seconds_since_epoch

def get_time_range_from_user(file_info):
    """
    Prompts the user to input a start and end time range in either seconds since epoch or datetime format.
    Args:
        file_info (dict): Information about the VDIF file, including the reference epoch.
    Returns:
        tuple: Start and end time in seconds since the VDIF file's reference epoch.
    """
    while True:
        try:
            print("Please enter the time range for the data retrieval.")
            start_time_str = input("Enter the start time (YYYY-MM-DD HH:MM:SS.sss or seconds since epoch): ")
            end_time_str = input("Enter the end time (YYYY-MM-DD HH:MM:SS.sss or seconds since epoch): ")

            start_seconds = parse_time_input(start_time_str, file_info)
            end_seconds = parse_time_input(end_time_str, file_info)

            break
        except:
            print("Incorrect format.")


    return start_seconds, end_seconds