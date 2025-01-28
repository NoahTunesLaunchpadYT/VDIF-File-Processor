import os
from PIL import Image

def png_to_pdf():
    # Get the current directory
    current_directory = os.getcwd()
    
    # Find all .png files in the current directory
    png_files = [f for f in os.listdir(current_directory) if f.endswith('.png')]
    
    if not png_files:
        print("No PNG files found in the current directory.")
        return
    
    # Sort the files alphabetically (optional)
    png_files.sort()
    
    # Create a list to hold the image objects
    images = []
    
    # Open each image and append it to the list
    for png_file in png_files:
        img_path = os.path.join(current_directory, png_file)
        img = Image.open(img_path)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        images.append(img)
    
    # Define the output PDF file path
    output_pdf_path = os.path.join(current_directory, 'output.pdf')
    
    # Save all images as a single PDF
    images[0].save(output_pdf_path, save_all=True, append_images=images[1:])
    
    print(f"PDF created successfully at {output_pdf_path}")

if __name__ == "__main__":
    png_to_pdf()