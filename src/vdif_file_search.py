import os

def format_file_size(bytes):
    """Convert file size in bytes to a human-readable string."""
    if bytes >= 1_000_000_000:
        return f"{bytes / 1_000_000_000:.2f} GB"
    elif bytes >= 1_000_000:
        return f"{bytes / 1_000_000:.2f} MB"
    else:
        return f"{bytes / 1_000:.2f} KB"
    
def get_vdif_file_path():
    # Search for .vdif files in the current directory
    vdif_files = [f for f in os.listdir('.') if f.lower().endswith('.vdif')]

    # Display indexed list of found files
    if vdif_files:
        print("Found the following .vdif files in the current directory:")
        print("0: Enter a custom path")
        for idx, file in enumerate(vdif_files, start=1):
            file_size = os.path.getsize(file)  # Get the file size in bytes
            readable_size = format_file_size(file_size)  # Convert to MB/GB
            print(f"{idx}: {file} ({readable_size})")
    else:
        print("No .vdif files found in the current directory.")
        print("You will need to enter a custom path.")

    # Allow user to select a file or provide a custom path
    while True:
        try:
            user_input = input("Enter the index of the file or 0 to provide a custom path: ")
            index = int(user_input)
            
            if index == 0:
                # User chooses to provide a custom path
                custom_path = input("Enter the path to the .vdif file: ")
                file = validate_vdif_file(custom_path)
                if file:
                    return file
            elif 1 <= index <= len(vdif_files):
                # Return the selected file
                print(f"Using file {index}: {vdif_files[index - 1]}")
                return vdif_files[index - 1]
            else:
                print("Invalid index. Please choose a valid number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def validate_vdif_file(file):
    # If the file path is empty, use a default value
    if file == "":
        print("Using default: GSSR_SHADOW_43XLCP_181-0320_8M_UL_8558M_frch_L_0540-0650.vdif")
        file = "GSSR_SHADOW_43XLCP_181-0320_8M_UL_8558M_frch_L_0540-0650.vdif"
    
    # Add ".vdif" extension if missing
    if not os.path.splitext(file)[1]:
        file += ".vdif"
    
    # Ensure the file extension is .vdif
    if os.path.splitext(file)[1].lower() != ".vdif":
        print("Invalid file type. Please enter a .vdif file.")
        return None

    # Check if the file exists and can be opened
    try:
        with open(file, 'rb'):
            return file
    except IOError:
        print(f"Unable to open the file '{file}'. Please check the file path.")
        return None
