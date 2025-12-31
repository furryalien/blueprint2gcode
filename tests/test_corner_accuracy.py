#!/usr/bin/env python3
"""
Test corner accuracy with various geometric shapes.
Generate test images with squares, rectangles, nested shapes, and rotated objects.
"""

import numpy as np
from PIL import Image, ImageDraw
import os

def create_test_images():
    """Create a series of test images with different geometric shapes."""
    
    output_dir = "../test_data/test_images_corners"
    os.makedirs(output_dir, exist_ok=True)
    
    # Standard size
    width, height = 800, 600
    
    tests = []
    
    # Test 1: Single square (centered)
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([250, 150, 550, 450], fill='black')
    tests.append(('test1_square_300x300.png', img, "300x300 square centered"))
    
    # Test 2: Single small square
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([350, 250, 450, 350], fill='black')
    tests.append(('test2_square_100x100.png', img, "100x100 small square"))
    
    # Test 3: Single large square
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 50, 700, 550], fill='black')
    tests.append(('test3_square_600x500.png', img, "600x500 large rectangle"))
    
    # Test 4: Wide rectangle
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 250, 700, 350], fill='black')
    tests.append(('test4_rect_wide_600x100.png', img, "600x100 wide rectangle"))
    
    # Test 5: Tall rectangle
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([350, 50, 450, 550], fill='black')
    tests.append(('test5_rect_tall_100x500.png', img, "100x500 tall rectangle"))
    
    # Test 6: Multiple squares (grid)
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 100, 200, 200], fill='black')
    draw.rectangle([300, 100, 400, 200], fill='black')
    draw.rectangle([500, 100, 600, 200], fill='black')
    draw.rectangle([100, 300, 200, 400], fill='black')
    draw.rectangle([300, 300, 400, 400], fill='black')
    draw.rectangle([500, 300, 600, 400], fill='black')
    tests.append(('test6_grid_6squares_100x100.png', img, "6 squares in grid (100x100 each)"))
    
    # Test 7: Nested squares
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 100, 700, 500], fill='black')
    draw.rectangle([200, 200, 600, 400], fill='white')
    draw.rectangle([300, 250, 500, 350], fill='black')
    tests.append(('test7_nested_squares.png', img, "Nested squares with holes"))
    
    # Test 8: Various sized rectangles
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 150, 100], fill='black')    # 100x50
    draw.rectangle([200, 50, 350, 100], fill='black')   # 150x50
    draw.rectangle([400, 50, 600, 100], fill='black')   # 200x50
    draw.rectangle([50, 150, 150, 250], fill='black')   # 100x100
    draw.rectangle([200, 150, 350, 300], fill='black')  # 150x150
    draw.rectangle([400, 150, 600, 350], fill='black')  # 200x200
    tests.append(('test8_various_sizes.png', img, "Various sized rectangles"))
    
    # Test 9: Rotated square (diamond)
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    # Diamond shape (rotated square)
    points = [(400, 100), (700, 300), (400, 500), (100, 300)]
    draw.polygon(points, fill='black')
    tests.append(('test9_diamond.png', img, "Rotated square (diamond)"))
    
    # Test 10: Parallelogram
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    points = [(150, 150), (500, 150), (600, 450), (250, 450)]
    draw.polygon(points, fill='black')
    tests.append(('test10_parallelogram.png', img, "Parallelogram"))
    
    # Test 11: Trapezoid
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    points = [(200, 150), (600, 150), (650, 450), (150, 450)]
    draw.polygon(points, fill='black')
    tests.append(('test11_trapezoid.png', img, "Trapezoid"))
    
    # Test 12: L-shape
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    points = [(150, 150), (450, 150), (450, 300), (300, 300), (300, 450), (150, 450)]
    draw.polygon(points, fill='black')
    tests.append(('test12_lshape.png', img, "L-shaped polygon"))
    
    # Test 13: Plus/Cross shape
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([350, 100, 450, 500], fill='black')  # Vertical bar
    draw.rectangle([200, 250, 600, 350], fill='black')  # Horizontal bar
    tests.append(('test13_cross.png', img, "Cross/plus shape"))
    
    # Test 14: Tiny squares (stress test)
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    for i in range(10):
        for j in range(6):
            x = 50 + i * 70
            y = 50 + j * 80
            draw.rectangle([x, y, x+40, y+40], fill='black')
    tests.append(('test14_tiny_grid_60squares.png', img, "60 tiny squares (40x40 each)"))
    
    # Test 15: Corner precision test
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    # Four squares in corners
    draw.rectangle([50, 50, 200, 200], fill='black')      # Top-left
    draw.rectangle([600, 50, 750, 200], fill='black')     # Top-right
    draw.rectangle([50, 400, 200, 550], fill='black')     # Bottom-left
    draw.rectangle([600, 400, 750, 550], fill='black')    # Bottom-right
    tests.append(('test15_corner_squares.png', img, "Squares at image corners"))
    
    # Save all test images
    print(f"Creating {len(tests)} test images in {output_dir}/")
    print("=" * 70)
    for filename, image, description in tests:
        path = os.path.join(output_dir, filename)
        image.save(path)
        print(f"✓ {filename:<35} - {description}")
    
    print("=" * 70)
    print(f"All test images saved to {output_dir}/")
    return len(tests)

if __name__ == '__main__':
    count = create_test_images()
    print(f"\nCreated {count} test images for corner accuracy testing.")
    print("\nNext step: Run these through blueprint2gcode.py to check for corner issues.")
