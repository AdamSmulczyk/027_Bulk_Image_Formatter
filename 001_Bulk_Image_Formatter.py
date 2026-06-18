

#!/usr/bin/env python
# coding: utf-8
# Project: Bulk Image Formatter 
# -Change the dimensions and edit a large number of files

# 1.Find all JPG images in a folder
# 2.Crop them to 500x500 pixels (from the center)
# 3.Convert them to PNG format
# 4.Save the converted images

# In[1]:

import os
from PIL import Image
import argparse


# In[ ]:


def process_image(input_path, output_folder, size=(500, 500)):
    """
    Process a single image: crop to square and convert to PNG
    
    Args:
        input_path: Path to the input JPG file
        output_folder: Folder to save the output PNG file
        size: Tuple of (width, height) for the output image
    """
    try:
        # Open the image
        img = Image.open(input_path)
        
        # Get original dimensions
        width, height = img.size
        
        # Calculate crop box (centered)
        if width > height:
            # Landscape image
            left = (width - height) // 2
            top = 0
            right = left + height
            bottom = height
        else:
            # Portrait or square image
            left = 0
            top = (height - width) // 2
            right = width
            bottom = top + width
        
        # Crop to square
        img_cropped = img.crop((left, top, right, bottom))
        
        # Resize to target size
        img_resized = img_cropped.resize(size, Image.LANCZOS)
        
        # Generate output filename (change extension to .png)
        filename = os.path.basename(input_path)
        name_without_ext = os.path.splitext(filename)[0]
        output_filename = f"{name_without_ext}.png"
        output_path = os.path.join(output_folder, output_filename)
        
        # Save as PNG
        img_resized.save(output_path, "PNG")
        print(f"Processed: {filename} → {output_filename}")
        
        return True
    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False

def batch_process_images(input_folder, output_folder, size=(500, 500)):
    """
    Process all JPG images in the input folder
    
    Args:
        input_folder: Folder containing JPG images
        output_folder: Folder to save the output PNG files
        size: Tuple of (width, height) for the output images
    """
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output directory: {output_folder}")
    
    # Get all JPG files in the input folder
    jpg_extensions = ('.jpg', '.jpeg', '.JPG', '.JPEG')
    jpg_files = [f for f in os.listdir(input_folder) if f.endswith(jpg_extensions)]
    
    if not jpg_files:
        print(f"No JPG files found in {input_folder}")
        return
    
    print(f"Found {len(jpg_files)} JPG files to process...")
    
    # Process each file
    successful = 0
    for jpg_file in jpg_files:
        input_path = os.path.join(input_folder, jpg_file)
        if process_image(input_path, output_folder, size):
            successful += 1
    
    print(f"Processing complete. {successful} of {len(jpg_files)} images converted successfully.")

def main():
    parser = argparse.ArgumentParser(description='Convert JPG images to 500x500 PNG')
    parser.add_argument('input_folder', help='Folder containing JPG images')
    parser.add_argument('--output-folder', '-o', help='Folder to save PNG images (default: input_folder/converted)')
    parser.add_argument('--size', '-s', type=int, default=500, help='Size of the output square images (default: 500)')
    
    args = parser.parse_args()
    
    # If output folder not specified, create a "converted" subfolder
    if not args.output_folder:
        args.output_folder = os.path.join(args.input_folder, 'converted')
    
    # Process images
    batch_process_images(args.input_folder, args.output_folder, size=(args.size, args.size))

if __name__ == "__main__":
    main()

