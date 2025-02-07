import re

try:
    import predix_splitter as ps
except:
    from src import predix_splitter as ps
import matplotlib.pyplot as plt
from datetime import datetime

def plot_predix_data(data_dict):
    """
    Plots the data extracted from a PREDIX file.

    Args:
        data_dict (dict): A dictionary containing column labels and data.
    """
    # Extract column labels and data
    column_labels = data_dict["column_labels"]
    data = data_dict["data"]

    # Convert the U.T. column to datetime objects for plotting
    utc_times = [datetime.strptime(row[0], "%Y %b %d %H:%M:%S") for row in data]

    # Create a dictionary to map column labels to their data
    column_data = {label: [] for label in column_labels}
    for row in data:
        for i, value in enumerate(row):
            if i == 0:
                column_data[column_labels[i]].append(value)
            else:
                column_data[column_labels[i]].append(float(value))

    # # Create plots for each available column (except U.T.)
    # plt.figure(figsize=(12, 6 * len(column_labels)))  # Adjust figure size dynamically

    for i, label in enumerate(column_labels):
        if label == "U.T.":
            continue  # Skip the U.T. column (already used for the x-axis)

        plt.plot(utc_times, column_data[label], label=label)
        plt.xlabel("Time (U.T.)")
        plt.ylabel(label)
        plt.title(f"{label} vs Time (Plot {i}/{len(column_labels)-1})")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()


    # Adjust layout and display the plots

def extract_predix_data(file_path):
    """
    Extracts column labels and data from a PREDIX file.

    Args:
        file_path (str): Path to the PREDIX file.

    Returns:
        dict: A dictionary containing the column labels and the corresponding data.
    """
    with open(file_path, "r") as file:
        lines = file.readlines()

    # Flag to indicate when we've reached the data table
    data_started = False
    column_labels = []
    data = []

    for line in lines:
        # Check if the line starts with a datetime (indicating the start of the data table)
        if re.match(r"^\s*\d{4}\s+[A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}", line):
            data_started = True
            # Extract column labels if not already extracted
            if not column_labels:
                # The previous line contains the column labels
                # Ignore the first word ("RECEIVER") and split the rest
                column_labels = lines[lines.index(line) - 1].split()[1:]
            # Extract data from the current line
            # Combine year, month, and day into a single "U.T." column
            parts = line.split()
            utc_time = " ".join(parts[:4])  # Combine year, month, day, and time
            row_data = [utc_time] + parts[4:]  # Add the rest of the data
            data.append(row_data)

        # Stop processing if we encounter a line that doesn't match the datetime pattern
        elif data_started and not re.match(r"^\s*\d{4}\s+[A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}", line):
            break

    return {
        "column_labels": column_labels,
        "data": data
    }

def plot_predix_file():
    file = ps.find_and_select_txt_file()
    dict = extract_predix_data(file)
    plot_predix_data(dict)
    print("Done printing \n")

if __name__ == "__main__":
    plot_predix_file()
