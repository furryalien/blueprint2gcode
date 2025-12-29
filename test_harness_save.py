#!/usr/bin/env python3
"""
Test harness for blueprint2gcode
Processes test images and visualizes input vs G-code output
Saves visualizations as PNG files and optionally displays them
"""

import subprocess
import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from PIL import Image
import re


def parse_gcode(gcode_file):
    """Parse G-code file to extract drawing paths."""
    paths = []
    current_path = []
    pen_down = False
    current_x, current_y = 0, 0
    
    with open(gcode_file, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip comments and empty lines
            if line.startswith(';') or not line:
                continue
            
            # Extract X, Y coordinates from any movement command
            x_match = re.search(r'X([-\d.]+)', line)
            y_match = re.search(r'Y([-\d.]+)', line)
            
            if x_match and y_match:
                current_x = float(x_match.group(1))
                current_y = float(y_match.group(1))
                
                # If pen is down, add point to path
                if pen_down:
                    current_path.append((current_x, current_y))
            
            # Check for pen down/up (Z commands)
            if 'Z' in line:
                z_match = re.search(r'Z([-\d.]+)', line)
                if z_match:
                    z_val = float(z_match.group(1))
                    if z_val <= 0.5:  # Pen down
                        if not pen_down:
                            pen_down = True
                            current_path = [(current_x, current_y)]  # Start new path with current position
                    else:  # Pen up
                        if pen_down and current_path:
                            paths.append(current_path)
                            current_path = []
                        pen_down = False
    
    # Add last path if exists
    if current_path:
        paths.append(current_path)
    
    return paths


def visualize_comparison(input_image, gcode_file, test_name, output_image):
    """Display input image and G-code visualization side by side."""
    # Load input image
    img = Image.open(input_image)
    
    # Parse G-code
    paths = parse_gcode(gcode_file)
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle(f'Test: {test_name}', fontsize=16, fontweight='bold')
    
    # Left subplot: G-code visualization
    ax1.set_title('G-code Output', fontsize=14)
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3)
    
    # Draw A4 page outline
    a4_width, a4_height = 210, 297
    page = FancyBboxPatch((0, 0), a4_width, a4_height, 
                          boxstyle="round,pad=0", 
                          edgecolor='lightgray', 
                          facecolor='white',
                          linewidth=2,
                          linestyle='--')
    ax1.add_patch(page)
    
    # Draw all paths
    total_points = 0
    for path in paths:
        if len(path) < 2:
            continue
        xs, ys = zip(*path)
        ax1.plot(xs, ys, 'b-', linewidth=1.5, solid_capstyle='round')
        total_points += len(path)
    
    # Draw start point
    if paths and paths[0]:
        ax1.plot(paths[0][0][0], paths[0][0][1], 'go', markersize=10, 
                label='Start', zorder=5)
    
    # Draw end point
    if paths and paths[-1]:
        ax1.plot(paths[-1][-1][0], paths[-1][-1][1], 'ro', markersize=10, 
                label='End', zorder=5)
    
    ax1.legend()
    ax1.set_xlim(-10, a4_width + 10)
    ax1.set_ylim(-10, a4_height + 10)
    
    # Add statistics
    stats_text = f"Paths: {len(paths)}\nPoints: {total_points}"
    ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes,
            verticalalignment='top', bbox=dict(boxstyle='round', 
            facecolor='wheat', alpha=0.8), fontsize=10)
    
    # Right subplot: Input image
    ax2.set_title('Input Image', fontsize=14)
    ax2.imshow(img, cmap='gray' if img.mode == 'L' else None)
    ax2.axis('off')
    
    # Add image info
    img_info = f"Size: {img.width}x{img.height}px\nMode: {img.mode}"
    ax2.text(0.02, 0.98, img_info, transform=ax2.transAxes,
            verticalalignment='top', bbox=dict(boxstyle='round', 
            facecolor='lightblue', alpha=0.8), fontsize=10, color='black')
    
    plt.tight_layout()
    
    # Save to file
    plt.savefig(output_image, dpi=150, bbox_inches='tight')
    print(f"Saved visualization: {output_image}")
    plt.close(fig)


def run_conversion(input_file, output_file):
    """Run blueprint2gcode conversion."""
    cmd = [
        sys.executable, 
        'blueprint2gcode.py',
        str(input_file),
        str(output_file)
    ]
    
    print(f"\n{'='*70}")
    print(f"Processing: {input_file.name}")
    print(f"{'='*70}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error converting {input_file}:")
        print(result.stderr)
        return False
    
    print(result.stdout)
    return True


def create_summary_html(test_results, output_dir):
    """Create an HTML summary page with all visualizations."""
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Blueprint2GCode Test Results</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .test-result {
            background-color: white;
            margin: 20px 0;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .test-result h2 {
            color: #0066cc;
            margin-top: 0;
        }
        .test-result img {
            width: 100%;
            max-width: 1200px;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .summary {
            background-color: #e8f4f8;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <h1>Blueprint2GCode Test Results</h1>
    <p style="text-align: center; color: #666;">Generated on: """ + str(Path.cwd()) + """</p>
"""
    
    for test_name, viz_file in test_results:
        html += f"""
    <div class="test-result">
        <h2>{test_name}</h2>
        <img src="{viz_file.name}" alt="{test_name}">
    </div>
"""
    
    html += """
</body>
</html>
"""
    
    html_file = output_dir / 'test_results.html'
    with open(html_file, 'w') as f:
        f.write(html)
    
    print(f"\nCreated HTML summary: {html_file}")
    return html_file


def main():
    # Check if test images exist
    test_dir = Path('test_images')
    if not test_dir.exists():
        print("Test images not found. Generating them first...")
        subprocess.run([sys.executable, 'generate_test_images.py'])
        print()
    
    # Create output directories
    output_dir = Path('test_output')
    output_dir.mkdir(exist_ok=True)
    
    viz_dir = Path('test_visualizations')
    viz_dir.mkdir(exist_ok=True)
    
    # Find all test images
    test_images = sorted(test_dir.glob('test*.png'))
    
    if not test_images:
        print("No test images found!")
        return 1
    
    print(f"Found {len(test_images)} test images")
    print(f"G-code output: {output_dir}")
    print(f"Visualizations: {viz_dir}")
    
    test_results = []
    
    # Process each test image
    for test_image in test_images:
        output_file = output_dir / f"{test_image.stem}.gcode"
        viz_file = viz_dir / f"{test_image.stem}_comparison.png"
        
        # Run conversion
        success = run_conversion(test_image, output_file)
        
        if not success:
            continue
        
        # Visualize results
        try:
            visualize_comparison(test_image, output_file, test_image.stem, viz_file)
            test_results.append((test_image.stem, viz_file))
        except Exception as e:
            print(f"Error visualizing {test_image}: {e}")
            import traceback
            traceback.print_exc()
    
    # Create HTML summary
    if test_results:
        html_file = create_summary_html(test_results, viz_dir)
        print(f"\n{'='*70}")
        print("To view results, open:")
        print(f"  {html_file}")
        print(f"\nOr view individual images in: {viz_dir}")
    
    print(f"\n{'='*70}")
    print("All tests completed!")
    print(f"G-code files: {output_dir}")
    print(f"Visualizations: {viz_dir}")
    print(f"{'='*70}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
