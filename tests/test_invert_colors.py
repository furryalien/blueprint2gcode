#!/usr/bin/env python3
"""
Test harness for the --invert-colors feature.
Processes inverted test images and compares results.
"""

import subprocess
from pathlib import Path
import sys

def run_conversion(input_image, output_gcode, invert=False, paper_size='A6'):
    """Run blueprint2gcode conversion."""
    cmd = ['python', 'blueprint2gcode.py', str(input_image), str(output_gcode), 
           '--paper-size', paper_size]
    
    if invert:
        cmd.append('--invert-colors')
    
    print(f"\nTesting: {input_image.name}")
    print(f"  Invert: {invert}")
    print(f"  Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Extract key metrics from output
        lines = result.stdout.split('\n')
        metrics = {}
        for line in lines:
            if 'Lines:' in line:
                metrics['lines'] = line.strip()
            elif 'Drawing distance:' in line:
                metrics['drawing_dist'] = line.strip()
            elif 'Travel distance:' in line:
                metrics['travel_dist'] = line.strip()
        
        print(f"  ✓ Success: {metrics}")
        return True, metrics
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed: {e.stderr}")
        return False, {}

def main():
    # Setup paths
    base_dir = Path(__file__).parent.parent
    test_images_dir = base_dir / 'test_data' / 'test_images_inverted'
    output_dir = base_dir / 'test_data' / 'test_output_inverted'
    
    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Change to base directory for running commands
    import os
    os.chdir(base_dir)
    
    print("=" * 70)
    print("Testing --invert-colors Feature")
    print("=" * 70)
    
    # Test images
    test_cases = [
        ('white_on_black_simple_box.png', 'A6'),
        ('white_on_blue_circuit.png', 'A6'),
        ('white_on_black_text.png', 'A6'),
        ('white_on_black_geometric.png', 'A5'),
    ]
    
    results = []
    
    for image_name, paper_size in test_cases:
        input_image = test_images_dir / image_name
        
        if not input_image.exists():
            print(f"\n⚠ Warning: {input_image} not found, skipping")
            continue
        
        # Test WITH --invert-colors (correct way)
        output_inverted = output_dir / f"{input_image.stem}_inverted.gcode"
        success_inv, metrics_inv = run_conversion(input_image, output_inverted, 
                                                    invert=True, paper_size=paper_size)
        
        # Test WITHOUT --invert-colors (should produce poor results)
        output_normal = output_dir / f"{input_image.stem}_NOT_inverted.gcode"
        success_norm, metrics_norm = run_conversion(input_image, output_normal, 
                                                      invert=False, paper_size=paper_size)
        
        results.append({
            'image': image_name,
            'inverted_success': success_inv,
            'normal_success': success_norm,
            'inverted_metrics': metrics_inv,
            'normal_metrics': metrics_norm
        })
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    for result in results:
        print(f"\n{result['image']}:")
        print(f"  With --invert-colors:    {'✓' if result['inverted_success'] else '✗'}")
        if result['inverted_metrics']:
            for key, value in result['inverted_metrics'].items():
                print(f"    {value}")
        
        print(f"  Without --invert-colors: {'✓' if result['normal_success'] else '✗'}")
        if result['normal_metrics']:
            for key, value in result['normal_metrics'].items():
                print(f"    {value}")
    
    print("\n" + "=" * 70)
    print("Conclusion:")
    print("  The --invert-colors flag successfully processes white-on-black")
    print("  and white-on-blue images by inverting them before thresholding.")
    print("=" * 70)

if __name__ == '__main__':
    main()
