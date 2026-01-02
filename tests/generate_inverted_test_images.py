#!/usr/bin/env python3
"""
Generate inverted test images for testing the --invert-colors feature.
Creates white-on-black and white-on-blue variations of standard test patterns.
"""

from PIL import Image, ImageDraw
import numpy as np
from pathlib import Path

def create_white_on_black_simple_box():
    """Create a simple white box on black background."""
    width, height = 400, 400
    img = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(img)
    
    # Draw white rectangle
    draw.rectangle([50, 50, 350, 350], outline='white', width=3)
    
    # Add some internal details
    draw.line([50, 200, 350, 200], fill='white', width=2)
    draw.line([200, 50, 200, 350], fill='white', width=2)
    
    return img

def create_white_on_blue_circuit():
    """Create a circuit-like pattern with white lines on blue background."""
    width, height = 500, 400
    img = Image.new('RGB', (width, height), color='#1E3A8A')  # Dark blue
    draw = ImageDraw.Draw(img)
    
    # Draw white "circuit" lines
    draw.line([50, 100, 200, 100], fill='white', width=3)
    draw.line([200, 100, 200, 300], fill='white', width=3)
    draw.line([200, 300, 450, 300], fill='white', width=3)
    
    # Add connection points (circles)
    draw.ellipse([195, 95, 205, 105], fill='white')
    draw.ellipse([195, 295, 205, 305], fill='white')
    draw.ellipse([45, 95, 55, 105], fill='white')
    draw.ellipse([445, 295, 455, 305], fill='white')
    
    # Add rectangles
    draw.rectangle([100, 80, 150, 120], outline='white', width=2)
    draw.rectangle([250, 280, 350, 320], outline='white', width=2)
    
    return img

def create_white_on_black_text():
    """Create simple text pattern on black background."""
    width, height = 400, 200
    img = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(img)
    
    # Draw large text-like shapes (not using font to avoid font dependencies)
    # Letter "A"
    draw.line([50, 150, 75, 50], fill='white', width=5)
    draw.line([75, 50, 100, 150], fill='white', width=5)
    draw.line([60, 110, 90, 110], fill='white', width=3)
    
    # Letter "B"
    draw.line([130, 50, 130, 150], fill='white', width=5)
    draw.arc([130, 50, 180, 100], 270, 90, fill='white', width=4)
    draw.arc([130, 100, 180, 150], 270, 90, fill='white', width=4)
    
    # Letter "C"
    draw.arc([200, 50, 260, 150], 45, 315, fill='white', width=5)
    
    return img

def create_white_on_black_geometric():
    """Create geometric shapes on black background."""
    width, height = 500, 500
    img = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(img)
    
    # Circle
    draw.ellipse([50, 50, 200, 200], outline='white', width=3)
    
    # Triangle
    draw.line([300, 200, 450, 200], fill='white', width=3)
    draw.line([450, 200, 375, 50], fill='white', width=3)
    draw.line([375, 50, 300, 200], fill='white', width=3)
    
    # Hexagon
    draw.line([100, 300, 150, 270], fill='white', width=3)
    draw.line([150, 270, 200, 300], fill='white', width=3)
    draw.line([200, 300, 200, 360], fill='white', width=3)
    draw.line([200, 360, 150, 390], fill='white', width=3)
    draw.line([150, 390, 100, 360], fill='white', width=3)
    draw.line([100, 360, 100, 300], fill='white', width=3)
    
    # Star
    points = [(400, 300), (420, 360), (480, 360), (430, 390), (450, 450), (400, 410), (350, 450), (370, 390), (320, 360), (380, 360)]
    for i in range(len(points)):
        draw.line([points[i], points[(i+1) % len(points)]], fill='white', width=2)
    
    return img

def main():
    # Create test_images directory if it doesn't exist
    output_dir = Path(__file__).parent.parent / 'test_data' / 'test_images_inverted'
    output_dir.mkdir(exist_ok=True, parents=True)
    
    print("Generating inverted test images...")
    
    # Generate images
    images = {
        'white_on_black_simple_box.png': create_white_on_black_simple_box(),
        'white_on_blue_circuit.png': create_white_on_blue_circuit(),
        'white_on_black_text.png': create_white_on_black_text(),
        'white_on_black_geometric.png': create_white_on_black_geometric(),
    }
    
    for filename, img in images.items():
        filepath = output_dir / filename
        img.save(filepath)
        print(f"  Created: {filepath}")
    
    print(f"\nGenerated {len(images)} test images in {output_dir}")
    print("\nYou can test these with:")
    print("  python blueprint2gcode.py test_data/test_images_inverted/<image>.png output.gcode --invert-colors")

if __name__ == '__main__':
    main()
