#!/usr/bin/env python3
"""
Comprehensive Regression Test Suite for blueprint2gcode

This test suite encompasses all existing test cases and provides:
- Automated test execution for all test categories
- Comprehensive validation of outputs
- HTML report generation with visual comparisons
- Performance metrics and statistics
- Pass/fail determination for each test case

Test Categories:
1. Basic conversion tests (various geometric shapes)
2. Corner accuracy tests (sharp corners, nested shapes)
3. Solid area filling tests (hatching patterns)
4. Paper size tests (A4, A5, A6)
5. Orientation tests (auto, landscape, portrait)
6. Color inversion tests (white-on-black images)
7. Special character tests (letters, underscores)
8. Integration tests (combined features)

Usage:
    python3 regression_suite.py [options]

Options:
    --quick         Run quick subset of tests (faster)
    --category CAT  Run only specific category (basic, corners, solid, etc.)
    --skip-viz      Skip visualization generation
    --verbose       Show detailed output
"""

import subprocess
import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import argparse

# Matplotlib for visualization
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import numpy as np
import re


# =============================================================================
# CONFIGURATION
# =============================================================================

# Paper sizes with dimensions in mm
PAPER_SIZES = {
    'A4': (210, 297),
    'A5': (148, 210),
    'A6': (105, 148)
}

# Test categories and their configurations
TEST_CATEGORIES = {
    'basic': {
        'name': 'Basic Conversion Tests',
        'description': 'Standard geometric shapes and patterns',
        'image_dir': 'test_images',
        'output_dir': 'test_output',
        'viz_dir': 'test_visualizations',
        'tests': [
            'test1_simple_box.png',
            'test2_floor_plan.png',
            'test3_geometric.png',
            'test4_mechanical.png',
            'test5_circuit.png',
            'test7_geodesic_dome.png'
        ],
        'params': {}
    },
    'corners': {
        'name': 'Corner Accuracy Tests',
        'description': 'Sharp corners, nested shapes, rotations',
        'image_dir': 'test_images_corners',
        'output_dir': 'test_output_corners',
        'viz_dir': 'test_visualizations_corners',
        'tests': [
            'test1_square_300x300.png',
            'test2_square_100x100.png',
            'test6_grid_6squares_100x100.png',
            'test7_nested_squares.png',
            'test9_diamond.png'
        ],
        'params': {'--fill-solid-areas': None}
    },
    'solid': {
        'name': 'Solid Area Fill Tests',
        'description': 'Hatching patterns with different angles and spacing',
        'image_dir': 'test_images_solid',
        'output_dir': 'test_output_solid',
        'viz_dir': 'test_visualizations_solid',
        'tests': [
            ('test1_simple_shapes.png', {'--hatch-angle': '45', '--hatch-spacing': '2.0'}),
            ('test1_simple_shapes.png', {'--hatch-angle': '0', '--hatch-spacing': '2.0'}),
            ('test1_simple_shapes.png', {'--hatch-angle': '90', '--hatch-spacing': '2.0'}),
            ('test4_floor_plan_with_walls.png', {'--hatch-angle': '45', '--hatch-spacing': '1.5'}),
            ('test5_mechanical_part.png', {'--hatch-angle': '45', '--hatch-spacing': '1.5'}),
            ('test6_crescent_spiral.png', {'--hatch-angle': '45', '--hatch-spacing': '1.0'})
        ],
        'params': {'--fill-solid-areas': None, '--min-solid-area': '1'}
    },
    'letters': {
        'name': 'Letter and Character Tests',
        'description': 'Text characters including thin shapes like underscores',
        'image_dir': 'test_images_letters',
        'output_dir': 'test_output',
        'viz_dir': 'test_visualizations',
        'tests': [
            'letters.jpg'
        ],
        'params': {'--fill-solid-areas': None, '--hatch-spacing': '1.5', '--hatch-angle': '45', '--min-solid-area': '1'}
    },
    'inverted': {
        'name': 'Color Inversion Tests',
        'description': 'White-on-black images with --invert-colors',
        'image_dir': 'test_images_inverted',
        'output_dir': 'test_output_inverted',
        'viz_dir': 'test_visualizations_inverted',
        'tests': [
            'white_on_black_simple_box.png',
            'white_on_blue_circuit.png',
            'white_on_black_text.png'
        ],
        'params': {'--invert-colors': None}
    },
    'paper_sizes': {
        'name': 'Paper Size Tests',
        'description': 'Different paper sizes (A4, A5, A6)',
        'image_dir': 'test_images',
        'output_dir': 'test_output_a6',
        'viz_dir': 'test_visualizations_a6',
        'tests': [
            ('test1_simple_box.png', {'--paper-size': 'A6'}),
            ('test1_simple_box.png', {'--paper-size': 'A5'}),
            ('test2_floor_plan.png', {'--paper-size': 'A6'})
        ],
        'params': {}
    },
    'orientations': {
        'name': 'Orientation Tests',
        'description': 'Auto, landscape, and portrait orientations',
        'image_dir': 'test_images',
        'output_dir': 'test_output_all_auto',
        'viz_dir': 'test_visualizations_all_auto',
        'tests': [
            ('test1_simple_box.png', {'--orientation': 'auto'}),
            ('test1_simple_box.png', {'--orientation': 'landscape'}),
            ('test1_simple_box.png', {'--orientation': 'portrait'}),
        ],
        'params': {'--paper-size': 'A6'}
    }
}


# =============================================================================
# G-CODE PARSING AND ANALYSIS
# =============================================================================

def parse_gcode(gcode_file: Path) -> Dict:
    """Parse G-code file and extract statistics and paths."""
    paths = []
    current_path = []
    pen_down = False
    current_x, current_y = 0, 0
    
    total_distance = 0
    travel_distance = 0
    
    with open(gcode_file, 'r') as f:
        for line in f:
            line = line.strip()
            
            if line.startswith(';') or not line:
                continue
            
            # Extract X, Y coordinates
            x_match = re.search(r'X([-\d.]+)', line)
            y_match = re.search(r'Y([-\d.]+)', line)
            
            prev_x, prev_y = current_x, current_y
            
            if x_match and y_match:
                current_x = float(x_match.group(1))
                current_y = float(y_match.group(1))
                
                # Calculate distance
                dist = ((current_x - prev_x)**2 + (current_y - prev_y)**2)**0.5
                
                if pen_down:
                    current_path.append((current_x, current_y))
                    total_distance += dist
                else:
                    travel_distance += dist
            
            # Check for pen down/up
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
    
    # Add last path if still drawing
    if len(current_path) > 1:
        paths.append(current_path)
    
    return {
        'paths': paths,
        'num_paths': len(paths),
        'total_distance': total_distance,
        'travel_distance': travel_distance
    }


def validate_gcode(gcode_file: Path, expected_min_paths: int = 1) -> Tuple[bool, str]:
    """Validate G-code output meets minimum requirements."""
    if not gcode_file.exists():
        return False, "Output file not created"
    
    if gcode_file.stat().st_size == 0:
        return False, "Output file is empty"
    
    try:
        stats = parse_gcode(gcode_file)
        
        if stats['num_paths'] < expected_min_paths:
            return False, f"Too few paths: {stats['num_paths']} < {expected_min_paths}"
        
        if stats['total_distance'] < 1.0:
            return False, f"Drawing distance too short: {stats['total_distance']:.2f}mm"
        
        return True, "Valid"
    
    except Exception as e:
        return False, f"Parse error: {str(e)}"


# =============================================================================
# VISUALIZATION
# =============================================================================

def create_visualization(input_image: Path, gcode_file: Path, output_image: Path, test_name: str):
    """Create side-by-side comparison visualization."""
    try:
        # Parse G-code
        stats = parse_gcode(gcode_file)
        paths = stats['paths']
        
        # Load input image
        img = Image.open(input_image)
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle(f'{test_name}\n{stats["num_paths"]} paths, {stats["total_distance"]:.1f}mm drawing distance',
                     fontsize=14, fontweight='bold')
        
        # Left: Input image
        ax1.imshow(img)
        ax1.set_title('Input Image', fontsize=12, fontweight='bold')
        ax1.axis('off')
        
        # Right: G-code output
        ax2.set_aspect('equal')
        ax2.invert_yaxis()
        ax2.set_facecolor('white')
        ax2.grid(True, alpha=0.2, linewidth=0.5)
        ax2.set_title('G-Code Output', fontsize=12, fontweight='bold')
        ax2.set_xlabel('X (mm)', fontsize=10)
        ax2.set_ylabel('Y (mm)', fontsize=10)
        
        # Draw all paths
        for path in paths:
            if len(path) < 2:
                continue
            xs = [p[0] for p in path]
            ys = [p[1] for p in path]
            ax2.plot(xs, ys, 'b-', linewidth=0.3, alpha=0.8)
        
        # Auto-scale
        if paths:
            all_points = [p for path in paths for p in path]
            if all_points:
                xs = [p[0] for p in all_points]
                ys = [p[1] for p in all_points]
                margin = 5
                ax2.set_xlim(min(xs) - margin, max(xs) + margin)
                ax2.set_ylim(min(ys) - margin, max(ys) + margin)
        
        plt.tight_layout()
        plt.savefig(output_image, dpi=120, bbox_inches='tight')
        plt.close()
        
        return True
    
    except Exception as e:
        print(f"  ⚠ Visualization failed: {e}")
        return False


# =============================================================================
# TEST EXECUTION
# =============================================================================

class TestResult:
    """Container for test results."""
    def __init__(self, name: str, category: str):
        self.name = name
        self.category = category
        self.passed = False
        self.error_message = ""
        self.execution_time = 0.0
        self.gcode_stats = {}
        self.visualization_path = None


def run_single_test(test_config: Dict, test_item, base_dir: Path, 
                   skip_viz: bool = False, verbose: bool = False) -> TestResult:
    """Execute a single test case."""
    
    # Parse test item
    if isinstance(test_item, tuple):
        test_file, extra_params = test_item
    else:
        test_file = test_item
        extra_params = {}
    
    # Setup paths
    input_path = base_dir / 'test_data' / test_config['image_dir'] / test_file
    output_filename = Path(test_file).stem + '_' + '_'.join(f"{k[2:]}_{v}" for k, v in extra_params.items() if v) + '.gcode'
    output_path = base_dir / 'test_data' / test_config['output_dir'] / output_filename
    viz_path = base_dir / 'visualizations' / test_config['viz_dir'] / (Path(test_file).stem + '.png')
    
    # Create result object
    test_name = f"{test_config['name']}: {test_file}"
    if extra_params:
        test_name += f" ({', '.join(f'{k}={v}' for k, v in extra_params.items())})"
    
    result = TestResult(test_name, test_config['name'])
    
    # Check if input exists
    if not input_path.exists():
        result.error_message = f"Input file not found: {input_path}"
        return result
    
    # Build command
    cmd = [
        'python3', str(base_dir / 'blueprint2gcode.py'),
        str(input_path),
        str(output_path)
    ]
    
    # Add base params from category
    for param, value in test_config['params'].items():
        cmd.append(param)
        if value is not None:
            cmd.append(str(value))
    
    # Add extra params for this specific test
    for param, value in extra_params.items():
        cmd.append(param)
        if value is not None:
            cmd.append(str(value))
    
    if verbose:
        print(f"  Command: {' '.join(cmd)}")
    
    # Execute conversion
    start_time = time.time()
    try:
        result_proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        result.execution_time = time.time() - start_time
        
        if result_proc.returncode != 0:
            result.error_message = f"Conversion failed: {result_proc.stderr[:200]}"
            return result
        
    except subprocess.TimeoutExpired:
        result.error_message = "Execution timeout (60s)"
        return result
    except Exception as e:
        result.error_message = f"Execution error: {str(e)}"
        return result
    
    # Validate output
    valid, msg = validate_gcode(output_path)
    if not valid:
        result.error_message = f"Validation failed: {msg}"
        return result
    
    # Get statistics
    result.gcode_stats = parse_gcode(output_path)
    
    # Create visualization
    if not skip_viz:
        viz_path.parent.mkdir(parents=True, exist_ok=True)
        result.visualization_path = viz_path
        create_visualization(input_path, output_path, viz_path, test_name)
    
    result.passed = True
    return result


def run_test_category(category_key: str, category_config: Dict, base_dir: Path,
                     skip_viz: bool = False, verbose: bool = False) -> List[TestResult]:
    """Run all tests in a category."""
    print(f"\n{'='*80}")
    print(f"{category_config['name']}")
    print(f"{category_config['description']}")
    print(f"{'='*80}")
    
    # Create output directories
    (base_dir / 'test_data' / category_config['output_dir']).mkdir(parents=True, exist_ok=True)
    (base_dir / 'visualizations' / category_config['viz_dir']).mkdir(parents=True, exist_ok=True)
    
    results = []
    
    for i, test_item in enumerate(category_config['tests'], 1):
        if isinstance(test_item, tuple):
            test_name = test_item[0]
        else:
            test_name = test_item
        
        print(f"\n[{i}/{len(category_config['tests'])}] Testing: {test_name}")
        
        result = run_single_test(category_config, test_item, base_dir, skip_viz, verbose)
        results.append(result)
        
        if result.passed:
            print(f"  ✓ PASS ({result.execution_time:.2f}s) - {result.gcode_stats['num_paths']} paths, "
                  f"{result.gcode_stats['total_distance']:.1f}mm")
        else:
            print(f"  ✗ FAIL: {result.error_message}")
    
    return results


# =============================================================================
# REPORT GENERATION
# =============================================================================

def generate_html_report(all_results: Dict[str, List[TestResult]], base_dir: Path, output_file: Path):
    """Generate comprehensive HTML report."""
    
    total_tests = sum(len(results) for results in all_results.values())
    passed_tests = sum(1 for results in all_results.values() for r in results if r.passed)
    failed_tests = total_tests - passed_tests
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>blueprint2gcode - Regression Test Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 36px;
        }}
        .header .timestamp {{
            opacity: 0.9;
            font-size: 14px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .summary-card .number {{
            font-size: 48px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .summary-card .label {{
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .passed {{ color: #10b981; }}
        .failed {{ color: #ef4444; }}
        .total {{ color: #3b82f6; }}
        .category {{
            background: white;
            padding: 25px;
            margin-bottom: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .category h2 {{
            margin-top: 0;
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        .test-result {{
            border-left: 4px solid #ddd;
            padding: 15px;
            margin: 10px 0;
            background: #fafafa;
            border-radius: 4px;
        }}
        .test-result.pass {{
            border-left-color: #10b981;
            background: #f0fdf4;
        }}
        .test-result.fail {{
            border-left-color: #ef4444;
            background: #fef2f2;
        }}
        .test-name {{
            font-weight: bold;
            font-size: 16px;
            margin-bottom: 8px;
        }}
        .test-stats {{
            font-size: 14px;
            color: #666;
            margin: 5px 0;
        }}
        .test-error {{
            color: #dc2626;
            font-family: monospace;
            font-size: 13px;
            background: white;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
        }}
        .visualization {{
            margin-top: 15px;
            max-width: 100%;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .badge.pass {{
            background: #10b981;
            color: white;
        }}
        .badge.fail {{
            background: #ef4444;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>blueprint2gcode - Regression Test Report</h1>
        <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
    </div>
    
    <div class="summary">
        <div class="summary-card">
            <div class="label">Total Tests</div>
            <div class="number total">{total_tests}</div>
        </div>
        <div class="summary-card">
            <div class="label">Passed</div>
            <div class="number passed">{passed_tests}</div>
        </div>
        <div class="summary-card">
            <div class="label">Failed</div>
            <div class="number failed">{failed_tests}</div>
        </div>
        <div class="summary-card">
            <div class="label">Success Rate</div>
            <div class="number" style="color: {'#10b981' if failed_tests == 0 else '#f59e0b'}">
                {(passed_tests/total_tests*100) if total_tests > 0 else 0:.1f}%
            </div>
        </div>
    </div>
"""
    
    # Add each category
    for category_name, results in all_results.items():
        category_passed = sum(1 for r in results if r.passed)
        category_total = len(results)
        
        html += f"""
    <div class="category">
        <h2>{TEST_CATEGORIES[category_name]['name']} 
            <span style="float: right; font-size: 18px; color: #666;">
                {category_passed}/{category_total} passed
            </span>
        </h2>
        <p style="color: #666; margin-bottom: 20px;">{TEST_CATEGORIES[category_name]['description']}</p>
"""
        
        for result in results:
            status_class = 'pass' if result.passed else 'fail'
            badge_text = 'PASS' if result.passed else 'FAIL'
            
            html += f"""
        <div class="test-result {status_class}">
            <div class="test-name">
                <span class="badge {status_class}">{badge_text}</span>
                {result.name}
            </div>
"""
            
            if result.passed:
                html += f"""
            <div class="test-stats">
                ⏱️ Execution time: {result.execution_time:.2f}s | 
                📏 Paths: {result.gcode_stats['num_paths']} | 
                🖊️ Drawing distance: {result.gcode_stats['total_distance']:.1f}mm | 
                ✈️ Travel distance: {result.gcode_stats['travel_distance']:.1f}mm
            </div>
"""
                if result.visualization_path and result.visualization_path.exists():
                    rel_path = result.visualization_path.relative_to(base_dir)
                    html += f"""
            <a href="../{rel_path}" target="_blank">
                <img src="../{rel_path}" class="visualization" />
            </a>
"""
            else:
                html += f"""
            <div class="test-error">Error: {result.error_message}</div>
"""
            
            html += """
        </div>
"""
        
        html += """
    </div>
"""
    
    html += """
</body>
</html>
"""
    
    with open(output_file, 'w') as f:
        f.write(html)


def generate_json_report(all_results: Dict[str, List[TestResult]], output_file: Path):
    """Generate JSON report for programmatic access."""
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total': sum(len(results) for results in all_results.values()),
            'passed': sum(1 for results in all_results.values() for r in results if r.passed),
            'failed': sum(1 for results in all_results.values() for r in results if not r.passed)
        },
        'categories': {}
    }
    
    for category_name, results in all_results.items():
        report['categories'][category_name] = {
            'name': TEST_CATEGORIES[category_name]['name'],
            'description': TEST_CATEGORIES[category_name]['description'],
            'total': len(results),
            'passed': sum(1 for r in results if r.passed),
            'tests': [
                {
                    'name': r.name,
                    'passed': r.passed,
                    'execution_time': r.execution_time,
                    'error': r.error_message if not r.passed else None,
                    'stats': r.gcode_stats if r.passed else None
                }
                for r in results
            ]
        }
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Comprehensive regression test suite for blueprint2gcode',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--quick', action='store_true',
                       help='Run quick subset of tests')
    parser.add_argument('--category', type=str, choices=list(TEST_CATEGORIES.keys()),
                       help='Run only specific category')
    parser.add_argument('--skip-viz', action='store_true',
                       help='Skip visualization generation')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed output')
    
    args = parser.parse_args()
    
    # Determine base directory
    base_dir = Path(__file__).parent.parent
    
    print("=" * 80)
    print("BLUEPRINT2GCODE - COMPREHENSIVE REGRESSION TEST SUITE")
    print("=" * 80)
    print(f"Base directory: {base_dir}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Determine which categories to run
    if args.category:
        categories_to_run = {args.category: TEST_CATEGORIES[args.category]}
    elif args.quick:
        # Quick mode: run subset of tests
        categories_to_run = {
            'basic': TEST_CATEGORIES['basic'],
            'corners': TEST_CATEGORIES['corners'],
            'solid': TEST_CATEGORIES['solid']
        }
    else:
        categories_to_run = TEST_CATEGORIES
    
    # Run tests
    all_results = {}
    start_time = time.time()
    
    for category_key, category_config in categories_to_run.items():
        results = run_test_category(category_key, category_config, base_dir, 
                                    args.skip_viz, args.verbose)
        all_results[category_key] = results
    
    total_time = time.time() - start_time
    
    # Calculate summary
    total_tests = sum(len(results) for results in all_results.values())
    passed_tests = sum(1 for results in all_results.values() for r in results if r.passed)
    failed_tests = total_tests - passed_tests
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests:    {total_tests}")
    print(f"Passed:         {passed_tests} ({'✓' if failed_tests == 0 else '⚠'})")
    print(f"Failed:         {failed_tests}")
    print(f"Success rate:   {(passed_tests/total_tests*100) if total_tests > 0 else 0:.1f}%")
    print(f"Total time:     {total_time:.2f}s")
    print(f"Average time:   {(total_time/total_tests) if total_tests > 0 else 0:.2f}s per test")
    
    # Generate reports
    print("\n" + "=" * 80)
    print("GENERATING REPORTS")
    print("=" * 80)
    
    report_dir = base_dir / 'test_data'
    html_report = report_dir / 'regression_test_report.html'
    json_report = report_dir / 'regression_test_report.json'
    
    generate_html_report(all_results, base_dir, html_report)
    print(f"✓ HTML report: {html_report}")
    
    generate_json_report(all_results, json_report)
    print(f"✓ JSON report: {json_report}")
    
    print("\n" + "=" * 80)
    
    # Exit with appropriate code
    sys.exit(0 if failed_tests == 0 else 1)


if __name__ == '__main__':
    main()
