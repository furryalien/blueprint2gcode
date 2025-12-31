#!/usr/bin/env python3
"""
Test harness for solid area filling functionality.
Tests different hatch patterns and parameters.
"""

import subprocess
import os
import time
from pathlib import Path

def create_output_directory():
    """Create directory for test output."""
    os.makedirs('test_output_solid', exist_ok=True)

def run_test(input_file, output_file, extra_args=None):
    """Run blueprint2gcode with specified parameters."""
    cmd = [
        'python3', 'blueprint2gcode.py',
        input_file,
        output_file,
        '--fill-solid-areas'
    ]
    
    if extra_args:
        cmd.extend(extra_args)
    
    print(f"\nRunning: {' '.join(cmd)}")
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        elapsed_time = time.time() - start_time
        print(f"✓ Completed in {elapsed_time:.2f}s")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed with error:")
        print(e.stderr)
        return False

def main():
    """Run all tests."""
    print("=" * 80)
    print("SOLID AREA FILLING TEST HARNESS")
    print("=" * 80)
    
    # Check if test images exist
    test_images_dir = Path('test_images_solid')
    if not test_images_dir.exists():
        print("\nTest images not found. Generating them first...")
        subprocess.run(['python3', 'generate_solid_test_images.py'], check=True)
    
    create_output_directory()
    
    # Test configurations
    tests = [
        # Basic tests with default parameters
        {
            'name': 'Test 1: Simple Shapes (Default Hatch)',
            'input': 'test_images_solid/test1_simple_shapes.png',
            'output': 'test_output_solid/test1_default.gcode',
            'args': []
        },
        {
            'name': 'Test 2: Mixed Solid/Outline (Default)',
            'input': 'test_images_solid/test2_mixed_solid_outline.png',
            'output': 'test_output_solid/test2_default.gcode',
            'args': []
        },
        
        # Different hatch angles
        {
            'name': 'Test 1: Horizontal Hatch (0°)',
            'input': 'test_images_solid/test1_simple_shapes.png',
            'output': 'test_output_solid/test1_hatch_0deg.gcode',
            'args': ['--hatch-angle', '0']
        },
        {
            'name': 'Test 1: Vertical Hatch (90°)',
            'input': 'test_images_solid/test1_simple_shapes.png',
            'output': 'test_output_solid/test1_hatch_90deg.gcode',
            'args': ['--hatch-angle', '90']
        },
        {
            'name': 'Test 1: Diagonal Hatch (135°)',
            'input': 'test_images_solid/test1_simple_shapes.png',
            'output': 'test_output_solid/test1_hatch_135deg.gcode',
            'args': ['--hatch-angle', '135']
        },
        
        # Different hatch spacing
        {
            'name': 'Test 1: Dense Hatch (0.5px)',
            'input': 'test_images_solid/test1_simple_shapes.png',
            'output': 'test_output_solid/test1_hatch_dense.gcode',
            'args': ['--hatch-spacing', '0.5']
        },
        {
            'name': 'Test 1: Sparse Hatch (3.0px)',
            'input': 'test_images_solid/test1_simple_shapes.png',
            'output': 'test_output_solid/test1_hatch_sparse.gcode',
            'args': ['--hatch-spacing', '3.0']
        },
        
        # Different minimum solid area
        {
            'name': 'Test 8: Small Details (min area 50px)',
            'input': 'test_images_solid/test8_small_details.png',
            'output': 'test_output_solid/test8_min_area_50.gcode',
            'args': ['--min-solid-area', '50']
        },
        {
            'name': 'Test 8: Small Details (min area 200px)',
            'input': 'test_images_solid/test8_small_details.png',
            'output': 'test_output_solid/test8_min_area_200.gcode',
            'args': ['--min-solid-area', '200']
        },
        {
            'name': 'Test 8: Small Details (min area 500px)',
            'input': 'test_images_solid/test8_small_details.png',
            'output': 'test_output_solid/test8_min_area_500.gcode',
            'args': ['--min-solid-area', '500']
        },
        
        # Complex real-world tests
        {
            'name': 'Test 3: Text with Solids',
            'input': 'test_images_solid/test3_text_with_solids.png',
            'output': 'test_output_solid/test3_text_solids.gcode',
            'args': []
        },
        {
            'name': 'Test 4: Floor Plan with Walls',
            'input': 'test_images_solid/test4_floor_plan_with_walls.png',
            'output': 'test_output_solid/test4_floor_plan.gcode',
            'args': ['--hatch-spacing', '2.0']
        },
        {
            'name': 'Test 5: Mechanical Part',
            'input': 'test_images_solid/test5_mechanical_part.png',
            'output': 'test_output_solid/test5_mechanical.gcode',
            'args': ['--hatch-angle', '45']
        },
        {
            'name': 'Test 6: Logo Style',
            'input': 'test_images_solid/test6_logo_style.png',
            'output': 'test_output_solid/test6_logo.gcode',
            'args': []
        },
        {
            'name': 'Test 7: Circuit with Pads',
            'input': 'test_images_solid/test7_circuit_with_pads.png',
            'output': 'test_output_solid/test7_circuit.gcode',
            'args': ['--hatch-spacing', '1.5']
        },
        
        # Paper size variations
        {
            'name': 'Test 1: Simple Shapes on A6',
            'input': 'test_images_solid/test1_simple_shapes.png',
            'output': 'test_output_solid/test1_a6.gcode',
            'args': ['--paper-size', 'A6']
        },
        {
            'name': 'Test 4: Floor Plan on A3',
            'input': 'test_images_solid/test4_floor_plan_with_walls.png',
            'output': 'test_output_solid/test4_floor_plan_a3.gcode',
            'args': ['--paper-size', 'A3', '--hatch-spacing', '1.5']
        },
    ]
    
    # Run all tests
    results = []
    for test in tests:
        print(f"\n{'=' * 80}")
        print(test['name'])
        print('=' * 80)
        success = run_test(test['input'], test['output'], test['args'])
        results.append({
            'name': test['name'],
            'success': success,
            'output': test['output']
        })
    
    # Summary
    print(f"\n{'=' * 80}")
    print("TEST SUMMARY")
    print('=' * 80)
    
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    print("\nResults:")
    for r in results:
        status = "✓ PASS" if r['success'] else "✗ FAIL"
        print(f"  {status} - {r['name']}")
        if r['success']:
            print(f"         Output: {r['output']}")
    
    print(f"\nAll output files saved to: test_output_solid/")
    
    # Comparison test without fill-solid-areas
    print(f"\n{'=' * 80}")
    print("COMPARISON: Testing WITHOUT --fill-solid-areas")
    print('=' * 80)
    
    cmd = [
        'python3', 'blueprint2gcode.py',
        'test_images_solid/test1_simple_shapes.png',
        'test_output_solid/test1_no_fill.gcode'
    ]
    print(f"\nRunning: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    
    print("\n" + "=" * 80)
    print("COMPARISON AVAILABLE:")
    print("  WITH filling:    test_output_solid/test1_default.gcode")
    print("  WITHOUT filling: test_output_solid/test1_no_fill.gcode")
    print("=" * 80)

if __name__ == '__main__':
    main()
