import os
from PIL import Image, ImageDraw, ImageFont
import argparse
import math

def add_watermark(img, text="Zeno", opacity=50):
    """
    Add a diagonal watermark to the image
    
    Args:
        img: PIL Image object
        text: Watermark text
        opacity: Watermark opacity (0-255)
    
    Returns:
        PIL Image with watermark
    """
    # Create a transparent overlay for the watermark
    watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    
    # Try to load a font, fall back to default if not found
    try:
        # Try to use a bold font if available
        font = ImageFont.truetype("Arial Bold.ttf", 80)
    except IOError:
        try:
            # Try Arial as fallback
            font = ImageFont.truetype("arial.ttf", 80)
        except IOError:
            # Use default font as last resort
            font = ImageFont.load_default()
    
    # Calculate text size and position - compatible with all Pillow versions
    # In newer Pillow versions, use getbbox, in older versions use getsize
    if hasattr(font, "getbbox"):
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    elif hasattr(draw, "textsize"):
        text_width, text_height = draw.textsize(text, font=font)
    else:
        text_width, text_height = font.getsize(text)
    
    # Create a new transparent image for the rotated text
    txt = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(txt)
    
    # Calculate text position to center it
    x = (img.width - text_width) // 2
    y = (img.height - text_height) // 2
    
    # Draw the text with specified opacity (alpha value)
    d.text((x, y), text, font=font, fill=(255, 255, 255, opacity))
    
    # Rotate the text layer
    txt = txt.rotate(45, expand=False, center=(img.width//2, img.height//2))
    
    # Ensure the image is in RGBA mode for alpha compositing
    if img.mode != 'RGBA':
        img_rgba = img.convert('RGBA')
    else:
        img_rgba = img
        
    # Composite the text layer onto the image
    result = Image.alpha_composite(img_rgba, txt)
    
    # Convert back to RGB for saving as PNG
    return result.convert('RGB')

def process_image(input_path, output_folder, size=(500, 500), watermark_text="Zeno"):
    """
    Process a single image: crop to square, add watermark, and convert to PNG
    
    Args:
        input_path: Path to the input JPG file
        output_folder: Folder to save the output PNG file
        size: Tuple of (width, height) for the output image
        watermark_text: Text to use as watermark
    """
    try:
        # Open the image
        img = Image.open(input_path)
        
        # Convert to RGB if needed (in case it's CMYK, grayscale, etc.)
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
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
        img_resized = img_cropped.resize(size, Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.ANTIALIAS)
        
        # Add watermark
        img_watermarked = add_watermark(img_resized, text=watermark_text)
        
        # Generate output filename (change extension to .png)
        filename = os.path.basename(input_path)
        name_without_ext = os.path.splitext(filename)[0]
        output_filename = f"{name_without_ext}.png"
        output_path = os.path.join(output_folder, output_filename)
        
        # Save as PNG
        img_watermarked.save(output_path, "PNG")
        print(f"Processed: {filename} → {output_filename}")
        
        return True
    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False

def batch_process_images(input_folder, output_folder, size=(500, 500), watermark_text="Zeno"):
    """
    Process all JPG images in the input folder
    
    Args:
        input_folder: Folder containing JPG images
        output_folder: Folder to save the output PNG files
        size: Tuple of (width, height) for the output images
        watermark_text: Text to use as watermark
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
        if process_image(input_path, output_folder, size, watermark_text):
            successful += 1
    
    print(f"Processing complete. {successful} of {len(jpg_files)} images converted successfully with '{watermark_text}' watermark.")

def main():
    parser = argparse.ArgumentParser(description='Convert JPG images to 500x500 PNG with watermark')
    parser.add_argument('input_folder', help='Folder containing JPG images')
    parser.add_argument('--output-folder', '-o', help='Folder to save PNG images (default: input_folder/converted)')
    parser.add_argument('--size', '-s', type=int, default=500, help='Size of the output square images (default: 500)')
    parser.add_argument('--watermark', '-w', default="Zeno", help='Watermark text (default: Zeno)')
    
    args = parser.parse_args()
    
    # If output folder not specified, create a "converted" subfolder
    if not args.output_folder:
        args.output_folder = os.path.join(args.input_folder, 'converted')
    
    # Process images
    batch_process_images(args.input_folder, args.output_folder, 
                         size=(args.size, args.size), 
                         watermark_text=args.watermark)

if __name__ == "__main__":
    main()
