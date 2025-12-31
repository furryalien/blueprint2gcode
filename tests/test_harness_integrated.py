#!/usr/bin/env python3
"""
Integrated Test Harness for blueprint2gcode
Includes solid area filling tests alongside regular tests
Shows input image and G-code output side-by-side
"""

import subprocess
import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import re
import time
from datetime import datetime


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


def extract_paper_size(gcode_file):
    """Extract paper size from G-code comments."""
    with open(gcode_file, 'r') as f:
        content = f.read()
    
    # Default to A4
    return 'A4'


def get_paper_dimensions(paper_size, orientation):
    """Get paper dimensions in mm."""
    sizes = {
        'A3': (297, 420),
        'A4': (210, 297),
        'A5': (148, 210),
        'A6': (105, 148)
    }
    
    width, height = sizes.get(paper_size, (210, 297))
    
    if orientation == 'landscape':
        return height, width
    return width, height


def visualize_comparison(input_image, gcode_file, test_name, output_file, paper_size='A4', orientation='auto'):
    """Create side-by-side visualization of input image and G-code output."""
    # Load original image
    img = Image.open(input_image)
    
    # Parse G-code
    paths = parse_gcode(gcode_file)
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Plot original image
    ax1.imshow(img, cmap='gray' if img.mode == 'L' else None)
    ax1.set_title(f'{test_name}\nOriginal Image ({img.width}x{img.height}px)', 
                  fontsize=12, fontweight='bold')
    ax1.axis('off')
    
    # Plot G-code paths
    ax2.set_aspect('equal')
    
    # Get paper dimensions
    paper_width, paper_height = get_paper_dimensions(paper_size, orientation)
    
    # Draw paper boundary
    paper_rect = patches.Rectangle((0, 0), paper_width, paper_height,
                                   linewidth=2, edgecolor='lightgray',
                                   facecolor='white', linestyle='--')
    ax2.add_patch(paper_rect)
    
    # Draw all paths
    for path in paths:
        if len(path) > 1:
            xs, ys = zip(*path)
            ax2.plot(xs, ys, 'b-', linewidth=0.5, alpha=0.8)
    
    # Count stats
    num_lines, distance = count_gcode_stats(gcode_file)
    
    ax2.set_xlim(-5, paper_width + 5)
    ax2.set_ylim(-5, paper_height + 5)
    ax2.set_title(f'{test_name}\nG-code Output ({paper_size} {orientation})\n' + 
                 f'{num_lines} lines, {distance:.1f}mm distance',
                 fontsize=12, fontweight='bold')
    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    return num_lines, distance


def run_single_test(test_config, results_list):
    """Run a single test configuration."""
    test_name = test_config['name']
    input_file = test_config['input']
    output_file = test_config['output']
    viz_file = test_config['viz']
    args = test_config.get('args', [])
    paper_size = test_config.get('paper_size', 'A4')
    orientation = test_config.get('orientation', 'auto')
    
    print(f"\n{'='*80}")
    print(f"Test: {test_name}")
    print('='*80)
    
    # Build command
    cmd = ['python3', '../blueprint2gcode.py', str(input_file), str(output_file)]
    if args:
        cmd.extend(args)
    
    print(f"Command: {' '.join(cmd)}")
    
    # Run conversion
    start_time = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        elapsed = time.time() - start_time
        
        if result.returncode != 0:
            print(f"✗ FAILED in {elapsed:.1f}s")
            print(result.stderr)
            results_list.append({
                'name': test_name,
                'status': 'FAILED',
                'time': elapsed,
                'error': result.stderr
            })
            return False
        
        print(f"✓ Conversion completed in {elapsed:.1f}s")
        
        # Create visualization
        num_lines, distance = visualize_comparison(
            input_file, output_file, test_name, viz_file, 
            paper_size, orientation
        )
        
        print(f"  Lines: {num_lines}, Distance: {distance:.1f}mm")
        print(f"  Visualization: {viz_file}")
        
        results_list.append({
            'name': test_name,
            'status': 'PASSED',
            'time': elapsed,
            'lines': num_lines,
            'distance': distance,
            'viz': viz_file,
            'gcode': output_file,
            'input': input_file
        })
        
        return True
        
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print(f"✗ TIMEOUT after {elapsed:.1f}s")
        results_list.append({
            'name': test_name,
            'status': 'TIMEOUT',
            'time': elapsed
        })
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"✗ ERROR: {e}")
        results_list.append({
            'name': test_name,
            'status': 'ERROR',
            'time': elapsed,
            'error': str(e)
        })
        return False


def generate_html_report(results, output_file):
    """Generate HTML report with all test results."""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Blueprint2GCode Test Results</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .summary {{
            background-color: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .test-result {{
            background-color: white;
            margin: 20px 0;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .status {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 3px;
            font-weight: bold;
        }}
        .status.passed {{ background-color: #4CAF50; color: white; }}
        .status.failed {{ background-color: #f44336; color: white; }}
        .status.timeout {{ background-color: #ff9800; color: white; }}
        .status.error {{ background-color: #9c27b0; color: white; }}
        .visualization {{
            margin-top: 10px;
            max-width: 100%;
            border: 1px solid #ddd;
            border-radius: 5px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }}
        .stat-item {{
            background-color: #f9f9f9;
            padding: 10px;
            border-left: 3px solid #4CAF50;
        }}
        .timestamp {{
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <h1>Blueprint2GCode Test Results</h1>
    <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
"""
    
    # Summary
    passed = sum(1 for r in results if r['status'] == 'PASSED')
    failed = sum(1 for r in results if r['status'] == 'FAILED')
    timeout = sum(1 for r in results if r['status'] == 'TIMEOUT')
    error = sum(1 for r in results if r['status'] == 'ERROR')
    total = len(results)
    total_time = sum(r['time'] for r in results)
    
    html += f"""
    <div class="summary">
        <h2>Summary</h2>
        <div class="stats">
            <div class="stat-item">
                <strong>Total Tests:</strong> {total}
            </div>
            <div class="stat-item" style="border-left-color: #4CAF50;">
                <strong>Passed:</strong> {passed}
            </div>
            <div class="stat-item" style="border-left-color: #f44336;">
                <strong>Failed:</strong> {failed}
            </div>
            <div class="stat-item" style="border-left-color: #ff9800;">
                <strong>Timeout:</strong> {timeout}
            </div>
            <div class="stat-item" style="border-left-color: #9c27b0;">
                <strong>Errors:</strong> {error}
            </div>
            <div class="stat-item">
                <strong>Total Time:</strong> {total_time:.1f}s ({total_time/60:.1f}min)
            </div>
        </div>
    </div>
"""
    
    # Individual test results
    for result in results:
        status_class = result['status'].lower()
        html += f"""
    <div class="test-result">
        <h3>{result['name']} <span class="status {status_class}">{result['status']}</span></h3>
        <p><strong>Time:</strong> {result['time']:.1f}s</p>
"""
        
        if result['status'] == 'PASSED':
            html += f"""
        <div class="stats">
            <div class="stat-item">
                <strong>Lines:</strong> {result['lines']}
            </div>
            <div class="stat-item">
                <strong>Distance:</strong> {result['distance']:.1f}mm
            </div>
            <div class="stat-item">
                <strong>Input:</strong> {Path(result['input']).name}
            </div>
            <div class="stat-item">
                <strong>Output:</strong> {Path(result['gcode']).name}
            </div>
        </div>
        <img src="{Path(result['viz']).name}" alt="Visualization" class="visualization">
"""
        elif 'error' in result:
            html += f"""
        <p style="color: red;"><strong>Error:</strong></p>
        <pre style="background-color: #fee; padding: 10px; border-radius: 3px;">{result['error']}</pre>
"""
        
        html += "    </div>\n"
    
    html += """
</body>
</html>
"""
    
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"\n{'='*80}")
    print(f"HTML report generated: {output_file}")
    print(f"{'='*80}")


def main():
    """Run integrated test suite."""
    print("=" * 80)
    print("INTEGRATED BLUEPRINT2GCODE TEST HARNESS")
    print("Including Regular Tests + Solid Area Filling Tests")
    print("=" * 80)
    
    # Check and generate test images if needed
    if not Path('../test_data/test_images').exists():
        print("\nGenerating regular test images..")
        subprocess.run(['python3', 'generate_test_images.py'], check=True)
    
    if not Path('../test_data/test_images_solid').exists():
        print("\nGenerating solid area test images..")
        subprocess.run(['python3', 'generate_solid_test_images.py'], check=True)
    
    # Create output directories
    output_dir = Path('../test_data/test_output_integrated')
    viz_dir = Path('../visualizations/test_visualizations_integrated')
    output_dir.mkdir(exist_ok=True)
    viz_dir.mkdir(exist_ok=True)
    
    # Define test configurations
    tests = []
    
    # Regular tests (selection of important ones)
    regular_tests = [
        ('../test_data/test_images/test1_simple_box.png', 'Test 1: Simple Box'),
        ('../test_data/test_images/test2_floor_plan.png', 'Test 2: Floor Plan'),
        ('../test_data/test_images/test5_circuit.png', 'Test 5: Circuit'),
        ('../test_data/test_images/test8_interlocking_gears.png', 'Test 8: Interlocking Gears'),
    ]
    
    for input_file, name in regular_tests:
        if Path(input_file).exists():
            tests.append({
                'name': name,
                'input': input_file,
                'output': output_dir / f"{Path(input_file).stem}.gcode",
                'viz': viz_dir / f"{Path(input_file).stem}.png",
                'args': [],
                'paper_size': 'A4',
                'orientation': 'auto'
            })
    
    # Solid area tests
    solid_tests = [
        ('../test_data/test_images_solid/test1_simple_shapes.png', 'Solid 1: Simple Shapes (No Fill)', []),
        ('../test_data/test_images_solid/test1_simple_shapes.png', 'Solid 1: Simple Shapes (With Fill)', 
         ['--fill-solid-areas', '--hatch-spacing', '1.5', '--hatch-angle', '45']),
        ('../test_data/test_images_solid/test2_mixed_solid_outline.png', 'Solid 2: Mixed (With Fill)', 
         ['--fill-solid-areas']),
        ('../test_data/test_images_solid/test4_floor_plan_with_walls.png', 'Solid 4: Floor Plan Walls (With Fill)', 
         ['--fill-solid-areas', '--hatch-spacing', '2.0']),
        ('../test_data/test_images_solid/test5_mechanical_part.png', 'Solid 5: Mechanical Part (With Fill)', 
         ['--fill-solid-areas', '--hatch-angle', '45']),
        ('../test_data/test_images_solid/test7_circuit_with_pads.png', 'Solid 7: Circuit Pads (With Fill)', 
         ['--fill-solid-areas', '--hatch-spacing', '1.5']),
        ('../test_data/test_images_solid/test8_small_details.png', 'Solid 8: Small Details (min 200px)', 
         ['--fill-solid-areas', '--min-solid-area', '200']),
    ]
    
    for i, (input_file, name, args) in enumerate(solid_tests):
        if Path(input_file).exists():
            stem = f"solid_{i+1}_{Path(input_file).stem}"
            tests.append({
                'name': name,
                'input': input_file,
                'output': output_dir / f"{stem}.gcode",
                'viz': viz_dir / f"{stem}.png",
                'args': args,
                'paper_size': 'A4',
                'orientation': 'auto'
            })
    
    # Run all tests
    results = []
    for test in tests:
        run_single_test(test, results)
    
    # Generate report
    report_file = viz_dir / 'test_report.html'
    generate_html_report(results, report_file)
    
    # Print summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print('='*80)
    passed = sum(1 for r in results if r['status'] == 'PASSED')
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"\nAll visualizations saved to: {viz_dir}/")
    print(f"All G-code files saved to: {output_dir}/")
    print(f"HTML Report: {report_file}")
    print('='*80)
    
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
