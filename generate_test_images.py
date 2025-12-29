#!/usr/bin/env python3
"""
Generate sample blueprint-style test images
"""

import numpy as np
from PIL import Image, ImageDraw
import math


def create_test_image_1_simple_box():
    """Simple rectangle with diagonal"""
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Rectangle
    draw.rectangle([100, 100, 700, 500], outline='black', width=3)
    
    # Diagonal
    draw.line([100, 100, 700, 500], fill='black', width=3)
    
    # Cross in center
    draw.line([400, 200, 400, 400], fill='black', width=2)
    draw.line([300, 300, 500, 300], fill='black', width=2)
    
    img.save('test_images/test1_simple_box.png')
    print("Created test1_simple_box.png")


def create_test_image_2_floor_plan():
    """Simple floor plan style"""
    img = Image.new('RGB', (1000, 800), color='white')
    draw = ImageDraw.Draw(img)
    
    # Outer walls
    draw.rectangle([50, 50, 950, 750], outline='black', width=4)
    
    # Interior walls
    draw.line([500, 50, 500, 750], fill='black', width=4)
    draw.line([50, 400, 950, 400], fill='black', width=4)
    
    # Doors (gaps will be separate lines)
    draw.line([200, 50, 200, 100], fill='black', width=2)
    draw.line([200, 150, 200, 400], fill='black', width=2)
    
    draw.line([700, 50, 700, 100], fill='black', width=2)
    draw.line([700, 150, 700, 400], fill='black', width=2)
    
    # Windows
    draw.rectangle([150, 45, 250, 55], outline='black', width=2)
    draw.rectangle([650, 45, 750, 55], outline='black', width=2)
    
    # Stairs
    for i in range(10):
        y = 450 + i * 25
        draw.line([100, y, 200, y], fill='black', width=2)
    
    img.save('test_images/test2_floor_plan.png')
    print("Created test2_floor_plan.png")


def create_test_image_3_geometric():
    """Geometric shapes"""
    img = Image.new('RGB', (800, 800), color='white')
    draw = ImageDraw.Draw(img)
    
    # Circle
    draw.ellipse([50, 50, 250, 250], outline='black', width=3)
    
    # Triangle
    draw.polygon([600, 50, 750, 250, 450, 250], outline='black', width=3)
    
    # Hexagon
    cx, cy, r = 400, 500, 150
    points = []
    for i in range(6):
        angle = math.pi / 3 * i
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append((x, y))
    draw.polygon(points, outline='black', width=3)
    
    # Star
    cx, cy, r1, r2 = 150, 550, 80, 40
    star_points = []
    for i in range(10):
        angle = math.pi / 5 * i - math.pi / 2
        r = r1 if i % 2 == 0 else r2
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        star_points.append((x, y))
    draw.polygon(star_points, outline='black', width=3)
    
    # Spiral
    cx, cy = 650, 550
    points = []
    for i in range(100):
        angle = i * 0.3
        r = 5 + i * 0.8
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append((x, y))
    draw.line(points, fill='black', width=2)
    
    img.save('test_images/test3_geometric.png')
    print("Created test3_geometric.png")


def create_test_image_4_mechanical():
    """Mechanical drawing style"""
    img = Image.new('RGB', (1000, 700), color='white')
    draw = ImageDraw.Draw(img)
    
    # Main part outline
    draw.rectangle([200, 200, 800, 500], outline='black', width=3)
    
    # Mounting holes
    holes = [(300, 300), (700, 300), (300, 400), (700, 400)]
    for x, y in holes:
        draw.ellipse([x-30, y-30, x+30, y+30], outline='black', width=2)
        # Cross hair
        draw.line([x-40, y, x+40, y], fill='black', width=1)
        draw.line([x, y-40, x, y+40], fill='black', width=1)
    
    # Center circle
    draw.ellipse([450, 300, 550, 400], outline='black', width=3)
    
    # Dimension lines
    draw.line([200, 150, 800, 150], fill='black', width=1)
    draw.line([200, 140, 200, 160], fill='black', width=1)
    draw.line([800, 140, 800, 160], fill='black', width=1)
    
    draw.line([150, 200, 150, 500], fill='black', width=1)
    draw.line([140, 200, 160, 200], fill='black', width=1)
    draw.line([140, 500, 160, 500], fill='black', width=1)
    
    # Hidden lines (dashed)
    for i in range(0, 600, 30):
        draw.line([200 + i, 350, 200 + i + 15, 350], fill='black', width=1)
    
    img.save('test_images/test4_mechanical.png')
    print("Created test4_mechanical.png")


def create_test_image_5_circuit():
    """Circuit diagram style"""
    img = Image.new('RGB', (900, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Resistor
    x, y = 100, 200
    draw.line([x, y, x+40, y], fill='black', width=2)
    draw.rectangle([x+40, y-15, x+120, y+15], outline='black', width=2)
    draw.line([x+120, y, x+160, y], fill='black', width=2)
    
    # Capacitor
    x, y = 100, 350
    draw.line([x, y, x+70, y], fill='black', width=2)
    draw.line([x+70, y-20, x+70, y+20], fill='black', width=3)
    draw.line([x+90, y-20, x+90, y+20], fill='black', width=3)
    draw.line([x+90, y, x+160, y], fill='black', width=2)
    
    # Connection lines
    draw.line([160, 200, 300, 200], fill='black', width=2)
    draw.line([300, 200, 300, 300], fill='black', width=2)
    draw.line([160, 350, 300, 350], fill='black', width=2)
    draw.line([300, 350, 300, 300], fill='black', width=2)
    
    # IC chip
    x, y = 400, 250
    draw.rectangle([x, y, x+120, y+100], outline='black', width=3)
    # Pins
    for i in range(4):
        pin_y = y + 20 + i * 25
        draw.line([x, pin_y, x-20, pin_y], fill='black', width=2)
        draw.line([x+120, pin_y, x+140, pin_y], fill='black', width=2)
    
    # Ground symbol
    x, y = 300, 400
    draw.line([x, 350, x, y], fill='black', width=2)
    draw.line([x-30, y, x+30, y], fill='black', width=3)
    draw.line([x-20, y+10, x+20, y+10], fill='black', width=2)
    draw.line([x-10, y+20, x+10, y+20], fill='black', width=2)
    
    # LED
    x, y = 650, 300
    draw.polygon([x, y-20, x, y+20, x+30, y], outline='black', width=2)
    draw.line([x+30, y-20, x+30, y+20], fill='black', width=2)
    draw.line([x-30, y, x, y], fill='black', width=2)
    draw.line([x+30, y, x+60, y], fill='black', width=2)
    
    # Arrows for LED
    draw.line([x+10, y-25, x+20, y-35], fill='black', width=1)
    draw.polygon([x+20, y-35, x+15, y-33, x+18, y-30], fill='black')
    
    img.save('test_images/test5_circuit.png')
    print("Created test5_circuit.png")


def create_test_image_6_text_labels():
    """Technical drawing with text labels and annotations"""
    img = Image.new('RGB', (1000, 800), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use different font sizes (will use default if fonts not available)
    try:
        from PIL import ImageFont
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        # Fallback to default font
        font_large = None
        font_medium = None
        font_small = None
        font_tiny = None
    
    # Title block
    draw.rectangle([50, 50, 950, 150], outline='black', width=3)
    draw.line([50, 100, 950, 100], fill='black', width=2)
    draw.line([500, 50, 500, 150], fill='black', width=2)
    
    # Title text
    draw.text((80, 65), "ASSEMBLY DRAWING", fill='black', font=font_large)
    draw.text((520, 70), "SCALE: 1:10", fill='black', font=font_medium)
    draw.text((520, 110), "DATE: 2025-12-28", fill='black', font=font_small)
    
    # Main part with dimensions
    part_x, part_y = 200, 300
    part_w, part_h = 600, 250
    draw.rectangle([part_x, part_y, part_x+part_w, part_y+part_h], outline='black', width=4)
    
    # Dimension lines with text
    # Horizontal dimension
    dim_y = part_y - 60
    draw.line([part_x, dim_y, part_x+part_w, dim_y], fill='black', width=2)
    draw.line([part_x, dim_y-10, part_x, dim_y+10], fill='black', width=2)
    draw.line([part_x+part_w, dim_y-10, part_x+part_w, dim_y+10], fill='black', width=2)
    # Arrow heads
    draw.polygon([part_x+10, dim_y, part_x, dim_y-5, part_x, dim_y+5], fill='black')
    draw.polygon([part_x+part_w-10, dim_y, part_x+part_w, dim_y-5, part_x+part_w, dim_y+5], fill='black')
    draw.text((part_x + part_w/2 - 40, dim_y - 35), "600mm", fill='black', font=font_medium)
    
    # Vertical dimension
    dim_x = part_x - 60
    draw.line([dim_x, part_y, dim_x, part_y+part_h], fill='black', width=2)
    draw.line([dim_x-10, part_y, dim_x+10, part_y], fill='black', width=2)
    draw.line([dim_x-10, part_y+part_h, dim_x+10, part_y+part_h], fill='black', width=2)
    # Arrow heads
    draw.polygon([dim_x, part_y+10, dim_x-5, part_y, dim_x+5, part_y], fill='black')
    draw.polygon([dim_x, part_y+part_h-10, dim_x-5, part_y+part_h, dim_x+5, part_y+part_h], fill='black')
    draw.text((dim_x - 50, part_y + part_h/2 - 20), "250mm", fill='black', font=font_medium)
    
    # Internal features with labels
    # Mounting holes
    holes = [
        (300, 370, "HOLE A"),
        (700, 370, "HOLE B"),
        (300, 480, "HOLE C"),
        (700, 480, "HOLE D")
    ]
    for x, y, label in holes:
        draw.ellipse([x-20, y-20, x+20, y+20], outline='black', width=2)
        # Center mark
        draw.line([x-25, y, x+25, y], fill='black', width=1)
        draw.line([x, y-25, x, y+25], fill='black', width=1)
        # Label with leader line
        draw.line([x+25, y-25, x+60, y-40], fill='black', width=1)
        draw.text((x+65, y-50), label, fill='black', font=font_small)
        draw.text((x+65, y-30), "Ø20mm", fill='black', font=font_tiny)
    
    # Notes section
    notes_y = 620
    draw.line([50, notes_y, 950, notes_y], fill='black', width=2)
    draw.text((60, notes_y + 10), "NOTES:", fill='black', font=font_medium)
    draw.text((60, notes_y + 50), "1. ALL DIMENSIONS IN MILLIMETERS", fill='black', font=font_small)
    draw.text((60, notes_y + 75), "2. MATERIAL: ALUMINUM 6061-T6", fill='black', font=font_small)
    draw.text((60, notes_y + 100), "3. TOLERANCES: ±0.1mm UNLESS NOTED", fill='black', font=font_small)
    
    # Part number callout
    draw.ellipse([480, 380, 520, 420], outline='black', width=2)
    draw.text((488, 390), "1", fill='black', font=font_medium)
    draw.line([520, 400, 580, 350], fill='black', width=1)
    draw.text((585, 335), "PART NO: A-12345", fill='black', font=font_small)
    
    img.save('test_images/test6_text_labels.png')
    print("Created test6_text_labels.png")


def main():
    import os
    os.makedirs('test_images', exist_ok=True)
    
    print("Generating test images...")
    create_test_image_1_simple_box()
    create_test_image_2_floor_plan()
    create_test_image_3_geometric()
    create_test_image_4_mechanical()
    create_test_image_5_circuit()
    create_test_image_6_text_labels()
    print("\nAll test images created in 'test_images/' directory")


if __name__ == '__main__':
    main()
