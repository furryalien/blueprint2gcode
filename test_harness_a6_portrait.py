#!/usr/bin/env python3
"""
Test harness for blueprint2gcode with A6 paper size in PORTRAIT orientation
Processes test images and visualizes input vs G-code output for A6 portrait format
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
    
    # Add final path if still drawing
    if pen_down and current_path:
        paths.append(current_path)
    
    return paths


def visualize_comparison(input_image, gcode_file, title, output_image):
    """Create side-by-side comparison of input image and G-code visualization."""
    # Parse G-code
    paths = parse_gcode(gcode_file)
    
    # Load input image
    img = Image.open(input_image)
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Plot G-code output (left) - A6 PORTRAIT is 105mm wide x 148mm high
    ax1.set_aspect('equal')
    ax1.set_title('G-code Output (A6 Portrait)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    ax1.grid(True, alpha=0.3)
    
    # Draw A6 paper boundary in portrait (105 x 148 mm)
    paper_rect = patches.Rectangle((0, 0), 105, 148, linewidth=2, 
                                   edgecolor='lightgray', facecolor='none',
                                   linestyle='--', label='A6 Portrait (105×148mm)')
    ax1.add_patch(paper_rect)
    
    # Plot all paths
    total_points = 0
    for path in paths:
        if path:
            xs, ys = zip(*path)
            ax1.plot(xs, ys, 'b-', linewidth=0.5)
            total_points += len(path)
    
    # Set axis limits to show full A6 portrait paper
    ax1.set_xlim(-5, 110)
    ax1.set_ylim(-5, 153)
    ax1.legend()
    
    # Plot input image (right)
    ax2.set_title('Input Image', fontsize=14, fontweight='bold')
    ax2.imshow(img, cmap='gray')
    ax2.axis('off')
    
    # Add statistics
    stats_text = f'Paths: {len(paths)} | Points: {total_points:,}'
    plt.figtext(0.5, 0.02, stats_text, ha='center', fontsize=10, 
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(output_image, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Saved visualization: {output_image}")


def run_conversion(input_file, output_file):
    """Run blueprint2gcode conversion with A6 paper size in PORTRAIT orientation."""
    cmd = [
        sys.executable, 
        'blueprint2gcode.py',
        str(input_file),
        str(output_file),
        '--paper-size', 'A6',
        '--orientation', 'portrait'
    ]
    
    print(f"\n{'='*70}")
    print(f"Processing: {input_file.name} (A6 Portrait)")
    print(f"{'='*70}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error converting {input_file}:")
        print(result.stderr)
        return False
    
    print(result.stdout)
    return True


def create_summary_html(test_results, output_dir):
    """Create an HTML summary page with all A6 portrait visualizations."""
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Blueprint2GCode A6 Portrait Test Results</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
            padding: 20px;
        }
        .header-info {
            text-align: center;
            color: #666;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .paper-info {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin: 20px auto;
            max-width: 800px;
        }
        .paper-info h2 {
            margin: 0 0 10px 0;
        }
        .orientation-badge {
            background-color: rgba(255, 255, 255, 0.3);
            padding: 5px 15px;
            border-radius: 20px;
            display: inline-block;
            margin-top: 10px;
            font-weight: bold;
        }
        .test-result {
            background-color: white;
            margin: 20px 0;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .test-result h2 {
            color: #4facfe;
            margin-top: 0;
            border-bottom: 2px solid #4facfe;
            padding-bottom: 10px;
        }
        .test-result img {
            width: 100%;
            max-width: 1400px;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .test-result img:hover {
            transform: scale(1.02);
        }
        .summary {
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        .footer {
            text-align: center;
            color: #888;
            margin-top: 40px;
            padding: 20px;
            border-top: 1px solid #ddd;
        }
    </style>
</head>
<body>
    <h1>🖨️ Blueprint2GCode Test Results</h1>
    <div class="paper-info">
        <h2>A6 Paper Format</h2>
        <div class="orientation-badge">📄 PORTRAIT ORIENTATION</div>
        <p style="margin-top: 15px;">Dimensions: 105mm × 148mm (4.1" × 5.8")</p>
        <p>All images forced to portrait orientation with automatic rotation</p>
    </div>
    <div class="header-info">
        Generated on: """ + str(Path.cwd()) + """<br>
        Total test cases: """ + str(len(test_results)) + """
    </div>
"""
    
    for test_name, viz_file in test_results:
        html += f"""
    <div class="test-result">
        <h2>📋 {test_name}</h2>
        <img src="{viz_file.name}" alt="{test_name}" onclick="window.open('{viz_file.name}', '_blank')">
    </div>
"""
    
    html += """
    <div class="footer">
        <p>Click on any image to view full size</p>
        <p>All outputs in A6 Portrait format (105mm × 148mm)</p>
        <p>Generated by blueprint2gcode test harness</p>
    </div>
</body>
</html>
"""
    
    html_file = output_dir / 'test_results_a6_portrait.html'
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
    output_dir = Path('test_output_a6_portrait')
    output_dir.mkdir(exist_ok=True)
    
    viz_dir = Path('test_visualizations_a6_portrait')
    viz_dir.mkdir(exist_ok=True)
    
    # Find all test images
    test_images = sorted(test_dir.glob('test*.png'))
    
    if not test_images:
        print("No test images found!")
        return 1
    
    print(f"Found {len(test_images)} test images")
    print(f"Paper size: A6 Portrait (105mm × 148mm)")
    print(f"Orientation: PORTRAIT (forced)")
    print(f"G-code output: {output_dir}")
    print(f"Visualizations: {viz_dir}")
    
    test_results = []
    
    # Process each test image
    for test_image in test_images:
        output_file = output_dir / f"{test_image.stem}_a6_portrait.gcode"
        viz_file = viz_dir / f"{test_image.stem}_a6_portrait_comparison.png"
        
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
        print("✓ All tests completed!")
        print(f"\nTo view results, open:")
        print(f"  {html_file}")
        print(f"\nOr view individual images in: {viz_dir}")
        print(f"\nG-code files in: {output_dir}")
    
    print(f"{'='*70}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
