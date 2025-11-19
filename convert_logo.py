#!/usr/bin/env python3
"""
Logo Conversion Script
Converts HEIC logo to PNG format for web use
"""

import sys
import os

def convert_heic_to_png(input_file, output_file):
    """Convert HEIC to PNG using PIL and pillow-heif"""
    try:
        from PIL import Image
        import pillow_heif

        print(f"Converting {input_file} to {output_file}...")

        # Register HEIF opener
        pillow_heif.register_heif_opener()

        # Open and convert
        image = Image.open(input_file)

        # Convert to RGBA if needed (for transparency)
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Save as PNG
        image.save(output_file, 'PNG')

        print(f"✓ Successfully converted to {output_file}")
        print(f"✓ Image size: {image.size[0]}x{image.size[1]} pixels")

        return True

    except ImportError:
        print("ERROR: Required libraries not installed.")
        print("Please install: pip install pillow pillow-heif")
        return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

def main():
    """Main conversion function"""

    # Default paths
    input_file = "whitelariatlogoblkbg.heic"
    output_file = "static/images/lariat-logo-white.png"

    # Check for command line arguments
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"ERROR: Input file '{input_file}' not found!")
        print("\nUsage:")
        print(f"  python convert_logo.py [input_file] [output_file]")
        print(f"\nExample:")
        print(f"  python convert_logo.py ~/Downloads/whitelariatlogoblkbg.heic static/images/lariat-logo-white.png")
        return False

    # Create output directory if needed
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    # Convert
    success = convert_heic_to_png(input_file, output_file)

    if success:
        print("\n" + "="*50)
        print("LOGO CONVERSION COMPLETE!")
        print("="*50)
        print(f"\nYour logo is ready at: {output_file}")
        print("\nNext steps:")
        print("1. Start the app: python app.py")
        print("2. Visit http://localhost:5000")
        print("3. Your logo should appear in the navigation bar!")
        print("\nIf logo doesn't appear, make sure the file is named:")
        print("  static/images/lariat-logo-white.png")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
