#!/usr/bin/env python3
"""
Generate test images with solid black areas for testing fill/hatch functionality.
"""

from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

def create_test_directory():
    """Create directory for test images if it doesn't exist."""
    os.makedirs('test_images_solid', exist_ok=True)

def test1_simple_shapes():
    """Test 1: Simple solid shapes - circle, square, triangle."""
    width, height = 800, 600
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Solid circle
    draw.ellipse([50, 50, 250, 250], fill='black')
    
    # Solid square
    draw.rectangle([300, 50, 500, 250], fill='black')
    
    # Solid triangle
    draw.polygon([(600, 250), (750, 250), (675, 50)], fill='black')
    
    # Some outline shapes for contrast
    draw.ellipse([50, 300, 250, 500], outline='black', width=3)
    draw.rectangle([300, 300, 500, 500], outline='black', width=3)
    
    img.save('test_images_solid/test1_simple_shapes.png')
    print("Created test1_simple_shapes.png")

def test2_mixed_solid_outline():
    """Test 2: Mix of solid and outline elements."""
    width, height = 1000, 800
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Solid rectangle with outline border
    draw.rectangle([100, 100, 400, 300], fill='black')
    draw.rectangle([80, 80, 420, 320], outline='black', width=5)
    
    # Multiple small solid circles
    for i in range(5):
        x = 500 + i * 80
        y = 100 + (i % 2) * 100
        draw.ellipse([x, y, x+50, y+50], fill='black')
    
    # Solid polygon shape
    draw.polygon([(150, 400), (250, 350), (350, 400), (300, 500), (200, 500)], fill='black')
    
    # Lines connecting elements
    draw.line([(400, 200), (500, 125)], fill='black', width=3)
    draw.line([(400, 200), (500, 225)], fill='black', width=3)
    
    img.save('test_images_solid/test2_mixed_solid_outline.png')
    print("Created test2_mixed_solid_outline.png")

def test3_text_with_solids():
    """Test 3: Text labels with solid highlighting."""
    width, height = 1000, 600
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Try to get a font, fall back to default if not available
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Solid highlight rectangles
    draw.rectangle([50, 50, 450, 120], fill='black')
    draw.rectangle([50, 180, 450, 250], fill='black')
    
    # Text on white background
    draw.text((500, 50), "IMPORTANT", fill='black', font=font_large)
    draw.text((500, 180), "WARNING", fill='black', font=font_large)
    
    # Solid arrows
    # Arrow 1
    draw.polygon([(100, 350), (300, 350), (300, 300), (400, 400), (300, 500), (300, 450), (100, 450)], fill='black')
    
    # Arrow 2 (pointing right)
    draw.polygon([(500, 350), (700, 350), (700, 300), (800, 400), (700, 500), (700, 450), (500, 450)], fill='black')
    
    img.save('test_images_solid/test3_text_with_solids.png')
    print("Created test3_text_with_solids.png")

def test4_floor_plan_with_walls():
    """Test 4: Simple floor plan with solid walls."""
    width, height = 1000, 800
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Outer walls (thick/solid) - draw as filled rectangles
    wall_thickness = 20
    
    # Outer perimeter - 4 solid walls
    # Top wall
    draw.rectangle([100, 100, 900, 100+wall_thickness], fill='black')
    # Bottom wall
    draw.rectangle([100, 700-wall_thickness, 900, 700], fill='black')
    # Left wall
    draw.rectangle([100, 100, 100+wall_thickness, 700], fill='black')
    # Right wall
    draw.rectangle([900-wall_thickness, 100, 900, 700], fill='black')
    
    # Interior walls with solid fill
    # Vertical wall
    draw.rectangle([300-wall_thickness//2, 100, 300+wall_thickness//2, 400], fill='black')
    
    # Horizontal wall
    draw.rectangle([300, 400-wall_thickness//2, 700, 400+wall_thickness//2], fill='black')
    
    # Another vertical wall
    draw.rectangle([700-wall_thickness//2, 400, 700+wall_thickness//2, 700], fill='black')
    
    # Doors (gaps in walls shown with arcs)
    draw.arc([100, 300, 150, 350], 0, 90, fill='black', width=2)
    draw.line([(100, 325), (125, 300)], fill='black', width=2)
    
    # Windows (thin lines)
    draw.line([(450, 100), (550, 100)], fill='black', width=3)
    draw.line([(450, 103), (550, 103)], fill='black', width=3)
    
    # Room labels
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    draw.text((150, 200), "Living Room", fill='black', font=font)
    draw.text((500, 200), "Kitchen", fill='black', font=font)
    draw.text((150, 500), "Bedroom", fill='black', font=font)
    draw.text((750, 500), "Bath", fill='black', font=font)
    
    img.save('test_images_solid/test4_floor_plan_with_walls.png')
    print("Created test4_floor_plan_with_walls.png")

def test5_mechanical_part():
    """Test 5: Mechanical part with solid sections - SIMPLIFIED for sharp corners."""
    width, height = 1000, 800
    # Create using NumPy for pixel-perfect sharp corners
    img_array = np.ones((height, width), dtype=np.uint8) * 255  # White background
    
    # Main body (solid black rectangle) with perfectly sharp corners
    img_array[200:601, 100:801] = 0  # Fill with pure black (0)
    
    # Cut-out holes (white circles) using NumPy for sharp edges
    # Draw circles by computing distance from center
    def draw_circle(img, center_x, center_y, radius, value):
        y, x = np.ogrid[:img.shape[0], :img.shape[1]]
        mask = (x - center_x)**2 + (y - center_y)**2 <= radius**2
        img[mask] = value
    
    # Three circular holes
    draw_circle(img_array, 325, 375, 75, 255)  # Left hole
    draw_circle(img_array, 675, 375, 75, 255)  # Right hole
    draw_circle(img_array, 475, 525, 75, 255)  # Bottom hole
    
    # Convert to PIL and save (no additional drawing to avoid anti-aliasing)
    img = Image.fromarray(img_array, mode='L')
    img.save('test_images_solid/test5_mechanical_part.png')
    print("Created test5_mechanical_part.png")

def test6_logo_style():
    """Test 6: Logo-style design with solid elements."""
    width, height = 800, 800
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Outer circle outline
    draw.ellipse([50, 50, 750, 750], outline='black', width=5)
    
    # Inner solid shapes forming a pattern
    # Triangle
    draw.polygon([(400, 150), (550, 400), (250, 400)], fill='black')
    
    # Rectangles
    draw.rectangle([200, 450, 300, 650], fill='black')
    draw.rectangle([500, 450, 600, 650], fill='black')
    
    # Small circles
    draw.ellipse([350, 500, 450, 600], fill='black')
    
    # Decorative lines
    for angle in range(0, 360, 30):
        x1 = 400 + 280 * np.cos(np.radians(angle))
        y1 = 400 + 280 * np.sin(np.radians(angle))
        x2 = 400 + 320 * np.cos(np.radians(angle))
        y2 = 400 + 320 * np.sin(np.radians(angle))
        draw.line([(x1, y1), (x2, y2)], fill='black', width=3)
    
    img.save('test_images_solid/test6_logo_style.png')
    print("Created test6_logo_style.png")

def test7_circuit_with_pads():
    """Test 7: Circuit diagram with solid pads."""
    width, height = 1000, 800
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # IC chip (outline)
    draw.rectangle([300, 200, 700, 600], outline='black', width=3)
    
    # Solid connection pads on the chip
    pad_width = 30
    pad_height = 15
    
    # Left side pads
    for i in range(8):
        y = 225 + i * 50
        draw.rectangle([280-pad_width, y-pad_height//2, 280, y+pad_height//2], fill='black')
        draw.line([(280-pad_width, y), (200, y)], fill='black', width=2)
    
    # Right side pads
    for i in range(8):
        y = 225 + i * 50
        draw.rectangle([720, y-pad_height//2, 720+pad_width, y+pad_height//2], fill='black')
        draw.line([(720+pad_width, y), (800, y)], fill='black', width=2)
    
    # Resistors (small rectangles)
    draw.rectangle([140, 220, 180, 240], outline='black', width=2)
    draw.rectangle([140, 320, 180, 340], outline='black', width=2)
    
    # Capacitors (parallel lines)
    draw.line([(140, 420), (140, 440)], fill='black', width=3)
    draw.line([(150, 420), (150, 440)], fill='black', width=3)
    
    # Ground symbols (solid triangles)
    draw.polygon([(100, 550), (160, 550), (130, 590)], fill='black')
    
    img.save('test_images_solid/test7_circuit_with_pads.png')
    print("Created test7_circuit_with_pads.png")

def test8_small_details():
    """Test 8: Small solid details to test minimum area threshold."""
    width, height = 800, 600
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Various sizes of solid circles
    sizes = [5, 10, 15, 20, 30, 50, 80, 120]
    
    for i, size in enumerate(sizes):
        x = 100 + (i % 4) * 180
        y = 100 + (i // 4) * 250
        draw.ellipse([x, y, x+size, y+size], fill='black')
        
        # Label with size
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            font = ImageFont.load_default()
        draw.text((x, y+size+10), f"{size}px", fill='black', font=font)
    
    img.save('test_images_solid/test8_small_details.png')
    print("Created test8_small_details.png")

def main():
    """Generate all test images."""
    print("Generating test images with solid areas...")
    create_test_directory()
    
    test1_simple_shapes()
    test2_mixed_solid_outline()
    test3_text_with_solids()
    test4_floor_plan_with_walls()
    test5_mechanical_part()
    test6_logo_style()
    test7_circuit_with_pads()
    test8_small_details()
    
    print(f"\nAll test images created in test_images_solid/")
    print("\nTo test with hatching, use:")
    print("  python blueprint2gcode.py test_images_solid/test1_simple_shapes.png output.gcode --fill-solid-areas")
    print("\nAdjust hatching parameters:")
    print("  --hatch-spacing 2.0      # Spacing between hatch lines (pixels)")
    print("  --hatch-angle 45.0       # Angle of hatch lines (degrees)")
    print("  --min-solid-area 100.0   # Minimum area to fill (pixels)")

if __name__ == '__main__':
    main()
