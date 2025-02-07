import re
import os

def split_predix_file(input_filename):
    with open(input_filename, 'r') as file:
        content = file.read()
    
    sections = re.split(r'\n\s*\*{5} PROGRAM JPL/OSOD-PREDIX', content)
    
    if len(sections) <= 1:
        print("Only one section found, no splitting needed.")
        return
    
    print(f"Identified {len(sections)} sections")
    
    for i, section in enumerate(sections):
        
        label_match = re.search(r'\(LABEL = ([^\)]+)\)', section)
        transmitter_match = re.search(r'TRANSMITTER\s+COORDINATES - STATION # (\d+)', section)
        receiver_match = re.search(r'RECEIVER\s+COORDINATES - STATION # (\d+)', section)
        
        if label_match and transmitter_match and receiver_match:
            label = label_match.group(1).strip()
            transmitter = transmitter_match.group(1).strip()
            receiver = receiver_match.group(1).strip()
            filename = f"{label}.{transmitter}-{receiver}.txt"
            
            with open(filename, 'w') as output_file:
                if i == 0:
                    output_file.write(section)
                else:
                    output_file.write("                   ***** PROGRAM JPL/OSOD-PREDIX" + section)

                
            print(f"Saved: {filename}")
        else:
            print("Warning: Could not extract all required fields for a section.")

def find_and_select_txt_file():
    txt_files = [f for f in os.listdir() if f.endswith('.txt')]
    if not txt_files:
        print("No .txt files found in the current directory.")
        return None
    
    print("\nPlease select a PREDIX file to use.\nAvailable .txt files:")
    for i, file in enumerate(txt_files):
        print(f"{i}: {file}")
        
    while True:
        try:
            index = int(input("Enter the index of the file to process: "))
            print("")
            return txt_files[index]
        except (ValueError, IndexError):
            print("Invalid selection. Please select a valid file.")

def split_predix_UI():
    selected_file = find_and_select_txt_file()
    if selected_file:
        split_predix_file(selected_file)

if __name__ == "__main__":
    split_predix_UI()