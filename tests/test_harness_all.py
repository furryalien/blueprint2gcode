#!/usr/bin/env python3
"""
Master Test Harness for blueprint2gcode
Runs all test images with all three orientations (auto, landscape, portrait) on A6 paper
Generates comprehensive HTML report with all results
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
import time


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
                    if z_val == 0.0:  # Pen down
                        pen_down = True
                        current_path = [(current_x, current_y)]
                    else:  # Pen up
                        pen_down = False
                        if len(current_path) > 1:
                            paths.append(current_path)
                        current_path = []
    
    # Add last path if pen was still down
    if len(current_path) > 1:
        paths.append(current_path)
    
    return paths


def count_gcode_stats(gcode_file):
    """Count number of drawing moves and total distance."""
    paths = parse_gcode(gcode_file)
    total_lines = len(paths)
    total_distance = 0
    
    for path in paths:
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            total_distance += ((x2 - x1)**2 + (y2 - y1)**2)**0.5
    
    return total_lines, total_distance


def visualize_comparison(input_image, gcode_file, test_name, output_file, orientation):
    """Create side-by-side visualization of input image and G-code output."""
    # Load original image
    img = Image.open(input_image)
    
    # Parse G-code
    paths = parse_gcode(gcode_file)
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Plot original image
    ax1.imshow(img, cmap='gray')
    ax1.set_title(f'{test_name} - Original Image', fontsize=14, fontweight='bold')
    ax1.axis('off')
    
    # Plot G-code paths
    ax2.set_aspect('equal')
    
    # A6 dimensions: 105mm x 148mm
    if orientation == 'landscape':
        paper_width, paper_height = 148, 105
    else:  # portrait or auto
        paper_width, paper_height = 105, 148
    
    # Draw paper boundary
    paper_rect = patches.Rectangle((0, 0), paper_width, paper_height,
                                   linewidth=2, edgecolor='lightgray',
                                   facecolor='white', linestyle='--')
    ax2.add_patch(paper_rect)
    
    # Draw all paths
    for path in paths:
        if len(path) > 1:
            xs, ys = zip(*path)
            ax2.plot(xs, ys, 'b-', linewidth=0.5)
    
    # Count stats
    num_lines, distance = count_gcode_stats(gcode_file)
    
    ax2.set_xlim(-5, paper_width + 5)
    ax2.set_ylim(-5, paper_height + 5)
    ax2.invert_yaxis()  # Flip Y-axis to match G-code coordinates
    ax2.set_title(f'{test_name} - G-code Output ({orientation.title()})\n' + 
                 f'{num_lines} lines, {distance:.2f}mm total distance',
                 fontsize=14, fontweight='bold')
    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    return num_lines, distance


def run_single_test(test_image, test_name, output_dir, viz_dir, orientation):
    """Run a single test with specified orientation."""
    gcode_file = output_dir / f"{test_name}.gcode"
    viz_file = viz_dir / f"{test_name}.png"
    
    # Run converter
    cmd = [
        'python3', '../blueprint2gcode.py',
        str(test_image),
        str(gcode_file),
        '--paper-size', 'A6',
        '--orientation', orientation
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"  ❌ FAILED: {test_name}")
        print(f"  Error: {result.stderr}")
        return None
    
    # Generate visualization
    num_lines, distance = visualize_comparison(test_image, gcode_file, test_name, viz_file, orientation)
    
    print(f"  ✓ {test_name}: {num_lines} lines, {distance:.2f}mm")
    
    return {
        'name': test_name,
        'lines': num_lines,
        'distance': distance,
        'gcode': gcode_file,
        'viz': viz_file
    }


def generate_html_report(results_by_orientation, output_file):
    """Generate comprehensive HTML report with all test results."""
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>Blueprint2GCode - Complete Test Results</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(to bottom, #f5f7fa 0%, #c3cfe2 100%);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            border-bottom: 4px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        h2 {
            color: #34495e;
            margin-top: 40px;
            border-left: 5px solid #3498db;
            padding-left: 15px;
            background: rgba(52, 152, 219, 0.1);
            padding: 10px 15px;
            border-radius: 5px;
        }
        .summary {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .stat-card h3 {
            margin: 0 0 10px 0;
            font-size: 1.2em;
            opacity: 0.9;
        }
        .stat-card .value {
            font-size: 2em;
            font-weight: bold;
            margin: 5px 0;
        }
        .test-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .test-card {
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: transform 0.3s ease;
        }
        .test-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        .test-card img {
            width: 100%;
            height: auto;
            display: block;
            cursor: pointer;
        }
        .test-info {
            padding: 15px;
            background: #f8f9fa;
        }
        .test-info h3 {
            margin: 0 0 10px 0;
            color: #2c3e50;
            font-size: 1.1em;
        }
        .test-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            font-size: 0.9em;
        }
        .stat {
            background: white;
            padding: 8px;
            border-radius: 5px;
            border-left: 3px solid #3498db;
        }
        .stat strong {
            color: #2c3e50;
        }
        .orientation-section {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .orientation-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin-left: 10px;
        }
        .auto { background: #3498db; color: white; }
        .landscape { background: #2ecc71; color: white; }
        .portrait { background: #e74c3c; color: white; }
    </style>
</head>
<body>
    <h1>Blueprint2GCode - Complete Test Results</h1>
    <div class="summary">
        <h2>Overall Summary</h2>
        <div class="summary-grid">
"""
    
    # Calculate overall stats
    total_tests = 0
    total_lines = 0
    total_distance = 0
    
    for orientation, results in results_by_orientation.items():
        for result in results:
            total_tests += 1
            total_lines += result['lines']
            total_distance += result['distance']
    
    html += f"""
            <div class="stat-card">
                <h3>Total Tests</h3>
                <div class="value">{total_tests}</div>
            </div>
            <div class="stat-card">
                <h3>Total Drawing Lines</h3>
                <div class="value">{total_lines:,}</div>
            </div>
            <div class="stat-card">
                <h3>Total Distance</h3>
                <div class="value">{total_distance:,.0f} mm</div>
            </div>
            <div class="stat-card">
                <h3>Orientations Tested</h3>
                <div class="value">{len(results_by_orientation)}</div>
            </div>
        </div>
    </div>
"""
    
    # Add results for each orientation
    orientation_colors = {
        'auto': 'auto',
        'landscape': 'landscape',
        'portrait': 'portrait'
    }
    
    for orientation in ['auto', 'landscape', 'portrait']:
        if orientation not in results_by_orientation:
            continue
            
        results = results_by_orientation[orientation]
        orientation_lines = sum(r['lines'] for r in results)
        orientation_distance = sum(r['distance'] for r in results)
        
        html += f"""
    <div class="orientation-section">
        <h2>
            {orientation.title()} Orientation
            <span class="orientation-badge {orientation_colors[orientation]}">{len(results)} Tests</span>
        </h2>
        <div style="margin: 15px 0; padding: 10px; background: #ecf0f1; border-radius: 5px;">
            <strong>Orientation Summary:</strong> 
            {orientation_lines:,} lines, {orientation_distance:,.0f}mm total distance
        </div>
        <div class="test-grid">
"""
        
        for result in results:
            # Ensure we have a string path (could be Path or already relative)
            if isinstance(result['viz'], Path):
                viz_path = str(result['viz'])
            else:
                viz_path = result['viz']
            
            html += f"""
            <div class="test-card">
                <img src="{viz_path}" alt="{result['name']}" onclick="window.open('{viz_path}', '_blank')">
                <div class="test-info">
                    <h3>{result['name']}</h3>
                    <div class="test-stats">
                        <div class="stat">
                            <strong>Lines:</strong> {result['lines']:,}
                        </div>
                        <div class="stat">
                            <strong>Distance:</strong> {result['distance']:.2f} mm
                        </div>
                    </div>
                </div>
            </div>
"""
        
        html += """
        </div>
    </div>
"""
    
    html += """
</body>
</html>
"""
    
    with open(output_file, 'w') as f:
        f.write(html)


def main():
    print("=" * 80)
    print("MASTER TEST HARNESS - ALL ORIENTATIONS")
    print("=" * 80)
    
    # Define test images
    test_images = [
        ('../test_data/test_images/test1_simple_box.png', 'test1_simple_box'),
        ('../test_data/test_images/test2_floor_plan.png', 'test2_floor_plan'),
        ('../test_data/test_images/test3_geometric.png', 'test3_geometric'),
        ('../test_data/test_images/test4_mechanical.png', 'test4_mechanical'),
        ('../test_data/test_images/test5_circuit.png', 'test5_circuit'),
        ('../test_data/test_images/test6_text_labels.png', 'test6_text_labels'),
        ('../test_data/test_images/test7_geodesic_dome.png', 'test7_geodesic_dome'),
        ('../test_data/test_images/test8_interlocking_gears.png', 'test8_interlocking_gears'),
    ]
    
    # Define orientations to test
    orientations = ['auto', 'landscape', 'portrait']
    
    # Store all results
    results_by_orientation = {}
    
    # Track total time
    start_time = time.time()
    
    # Run tests for each orientation
    for orientation in orientations:
        print(f"\n{'=' * 80}")
        print(f"TESTING: {orientation.upper()} ORIENTATION")
        print(f"{'=' * 80}\n")
        
        # Create output directories
        output_dir = Path(f'../test_data/test_output_all_{orientation}')
        viz_dir = Path(f'../visualizations/test_visualizations_all_{orientation}')
        output_dir.mkdir(exist_ok=True)
        viz_dir.mkdir(exist_ok=True)
        
        results = []
        orientation_start = time.time()
        
        # Run each test
        for test_image, test_name in test_images:
            result = run_single_test(
                Path(test_image),
                test_name,
                output_dir,
                viz_dir,
                orientation
            )
            if result:
                results.append(result)
        
        orientation_time = time.time() - orientation_start
        results_by_orientation[orientation] = results
        
        # Print summary for this orientation
        total_lines = sum(r['lines'] for r in results)
        total_distance = sum(r['distance'] for r in results)
        print(f"\n{orientation.upper()} ORIENTATION SUMMARY:")
        print(f"  Tests: {len(results)}")
        print(f"  Total lines: {total_lines:,}")
        print(f"  Total distance: {total_distance:,.2f}mm")
        print(f"  Processing time: {orientation_time:.1f}s")
    
    # Generate combined HTML report
    print(f"\n{'=' * 80}")
    print("GENERATING COMPREHENSIVE HTML REPORT")
    print(f"{'=' * 80}\n")
    
    html_file = Path('../test_data/test_results_all.html')
    generate_html_report(results_by_orientation, html_file)
    
    total_time = time.time() - start_time
    
    # Print final summary
    print(f"\n{'=' * 80}")
    print("COMPLETE TEST SUITE FINISHED!")
    print(f"{'=' * 80}\n")
    
    total_tests = sum(len(results) for results in results_by_orientation.values())
    total_lines = sum(r['lines'] for results in results_by_orientation.values() for r in results)
    total_distance = sum(r['distance'] for results in results_by_orientation.values() for r in results)
    
    print(f"Total Tests Run: {total_tests}")
    print(f"Total Drawing Lines: {total_lines:,}")
    print(f"Total Drawing Distance: {total_distance:,.2f}mm")
    print(f"Total Processing Time: {total_time:.1f}s")
    print(f"Average Time per Test: {total_time/total_tests:.1f}s")
    print(f"\nHTML Report: {html_file}")
    print(f"\nView results at: http://localhost:8889/{html_file}")


if __name__ == '__main__':
    main()
