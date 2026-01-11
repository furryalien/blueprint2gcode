#!/usr/bin/env python3
"""
Test script for noise reduction feature.
Tests the impact of noise reduction on various noisy images.
"""

import sys
import os
import subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import json

# Add parent directory to path to import main script
sys.path.insert(0, str(Path(__file__).parent.parent))

def create_noisy_test_images(output_dir):
    """Create test images with different types of noise."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    images_created = []
    
    # 1. Clean rectangle (baseline)
    print("Creating clean rectangle...")
    img = Image.new('RGB', (400, 300), 'white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 75, 300, 225], outline='black', width=3)
    draw.line([100, 150, 300, 150], fill='black', width=2)
    path = output_dir / 'clean_rectangle.png'
    img.save(path)
    images_created.append(('clean_rectangle', path))
    
    # 2. Rectangle with salt & pepper noise
    print("Creating noisy rectangle (salt & pepper)...")
    img = Image.new('RGB', (400, 300), 'white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 75, 300, 225], outline='black', width=3)
    draw.line([100, 150, 300, 150], fill='black', width=2)
    # Add salt & pepper noise
    pixels = img.load()
    np.random.seed(42)
    for _ in range(2000):
        x, y = np.random.randint(0, 400), np.random.randint(0, 300)
        if np.random.random() > 0.5:
            pixels[x, y] = (0, 0, 0)  # pepper
        else:
            pixels[x, y] = (255, 255, 255)  # salt
    path = output_dir / 'noisy_salt_pepper.png'
    img.save(path)
    images_created.append(('noisy_salt_pepper', path))
    
    # 3. Rectangle with JPEG compression artifacts
    print("Creating noisy rectangle (JPEG artifacts)...")
    img = Image.new('RGB', (400, 300), 'white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 75, 300, 225], outline='black', width=3)
    draw.line([100, 150, 300, 150], fill='black', width=2)
    # Save as low-quality JPEG and reload
    temp_jpg = output_dir / 'temp_jpeg.jpg'
    img.save(temp_jpg, 'JPEG', quality=10)
    img = Image.open(temp_jpg)
    path = output_dir / 'noisy_jpeg_artifacts.png'
    img.save(path)
    temp_jpg.unlink()
    images_created.append(('noisy_jpeg_artifacts', path))
    
    # 4. Text with speckles (simulating dirty scan)
    print("Creating text with speckles...")
    img = Image.new('RGB', (500, 200), 'white')
    draw = ImageDraw.Draw(img)
    draw.text((20, 80), 'NOISE TEST', fill='black')
    # Add random speckles
    pixels = img.load()
    np.random.seed(42)
    for _ in range(1500):
        x, y = np.random.randint(0, 500), np.random.randint(0, 200)
        pixels[x, y] = (0, 0, 0)
    path = output_dir / 'text_with_speckles.png'
    img.save(path)
    images_created.append(('text_with_speckles', path))
    
    # 5. Circle with Gaussian noise
    print("Creating circle with Gaussian noise...")
    img = Image.new('RGB', (400, 400), 'white')
    draw = ImageDraw.Draw(img)
    draw.ellipse([100, 100, 300, 300], outline='black', width=4)
    # Add Gaussian noise
    img_array = np.array(img)
    noise = np.random.normal(0, 25, img_array.shape)
    noisy_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(noisy_array)
    path = output_dir / 'circle_gaussian_noise.png'
    img.save(path)
    images_created.append(('circle_gaussian_noise', path))
    
    # 6. Complex shape with tiny pinpricks
    print("Creating complex shape with pinpricks...")
    img = Image.new('RGB', (500, 400), 'white')
    draw = ImageDraw.Draw(img)
    # Draw a star shape
    star_points = [
        (250, 50), (280, 150), (380, 150), (300, 220),
        (330, 320), (250, 260), (170, 320), (200, 220),
        (120, 150), (220, 150), (250, 50)
    ]
    draw.polygon(star_points, outline='black', width=3)
    # Add many tiny pinpricks (1-2 pixel noise)
    pixels = img.load()
    np.random.seed(42)
    for _ in range(5000):
        x, y = np.random.randint(0, 500), np.random.randint(0, 400)
        size = np.random.randint(1, 3)
        for dx in range(size):
            for dy in range(size):
                if 0 <= x+dx < 500 and 0 <= y+dy < 400:
                    pixels[x+dx, y+dy] = (0, 0, 0)
    path = output_dir / 'star_with_pinpricks.png'
    img.save(path)
    images_created.append(('star_with_pinpricks', path))
    
    print(f"\nCreated {len(images_created)} test images in {output_dir}")
    return images_created


def run_conversion(input_path, output_path, enable_noise_reduction=False, 
                  blur_kernel=3, morph_kernel=2, morph_iterations=1,
                  min_line_length=0.5, simplify_epsilon=0.1):
    """Run the blueprint2gcode converter with specified parameters."""
    script_path = Path(__file__).parent.parent / 'blueprint2gcode.py'
    
    cmd = [
        sys.executable,
        str(script_path),
        str(input_path),
        str(output_path),
        '--paper-size', 'A6',
        '--min-line-length', str(min_line_length),
        '--simplify-epsilon', str(simplify_epsilon),
    ]
    
    if enable_noise_reduction:
        cmd.extend([
            '--enable-noise-reduction',
            '--gaussian-blur-kernel', str(blur_kernel),
            '--morph-kernel-size', str(morph_kernel),
            '--morph-iterations', str(morph_iterations)
        ])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)


def count_gcode_lines(gcode_path):
    """Count the number of G1 (draw) commands in a G-code file."""
    try:
        with open(gcode_path, 'r') as f:
            lines = f.readlines()
        
        draw_lines = sum(1 for line in lines if line.strip().startswith('G1') and 'Z' not in line)
        total_lines = len(lines)
        
        return draw_lines, total_lines
    except:
        return 0, 0


def analyze_gcode_quality(gcode_path):
    """Analyze G-code quality metrics."""
    try:
        with open(gcode_path, 'r') as f:
            lines = f.readlines()
        
        metrics = {
            'total_lines': len(lines),
            'draw_commands': 0,
            'travel_commands': 0,
            'very_short_moves': 0,  # < 0.1mm
            'short_moves': 0,       # < 0.5mm
            'total_draw_distance': 0.0,
            'total_travel_distance': 0.0,
            'avg_segment_length': 0.0
        }
        
        current_pos = [0.0, 0.0]
        segment_lengths = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('G1'):
                # Parse coordinates
                x, y = current_pos[0], current_pos[1]
                if 'X' in line:
                    x = float(line.split('X')[1].split()[0])
                if 'Y' in line:
                    y = float(line.split('Y')[1].split()[0])
                
                distance = np.sqrt((x - current_pos[0])**2 + (y - current_pos[1])**2)
                
                if 'Z' in line:
                    # Pen up/down command
                    metrics['travel_commands'] += 1
                else:
                    # Drawing command
                    metrics['draw_commands'] += 1
                    metrics['total_draw_distance'] += distance
                    segment_lengths.append(distance)
                    
                    if distance < 0.1:
                        metrics['very_short_moves'] += 1
                    if distance < 0.5:
                        metrics['short_moves'] += 1
                
                current_pos = [x, y]
        
        if segment_lengths:
            metrics['avg_segment_length'] = np.mean(segment_lengths)
        
        return metrics
    except Exception as e:
        print(f"Error analyzing G-code: {e}")
        return None


def run_tests():
    """Run all noise reduction tests."""
    print("=" * 70)
    print("NOISE REDUCTION TEST SUITE")
    print("=" * 70)
    
    # Create test images
    test_images_dir = Path(__file__).parent.parent / 'test_data' / 'test_images_noise'
    images = create_noisy_test_images(test_images_dir)
    
    # Create output directories
    output_no_reduction = Path(__file__).parent.parent / 'test_data' / 'test_output_noise_off'
    output_with_reduction = Path(__file__).parent.parent / 'test_data' / 'test_output_noise_on'
    output_no_reduction.mkdir(parents=True, exist_ok=True)
    output_with_reduction.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    print("\n" + "=" * 70)
    print("RUNNING CONVERSIONS")
    print("=" * 70)
    
    for name, image_path in images:
        print(f"\n{'─' * 70}")
        print(f"Testing: {name}")
        print(f"{'─' * 70}")
        
        result = {
            'name': name,
            'image_path': str(image_path)
        }
        
        # Test WITHOUT noise reduction
        print(f"  Converting WITHOUT noise reduction...")
        output_path_off = output_no_reduction / f'{name}.gcode'
        success, stdout, stderr = run_conversion(
            image_path, output_path_off,
            enable_noise_reduction=False
        )
        
        if success and output_path_off.exists():
            metrics_off = analyze_gcode_quality(output_path_off)
            result['without_reduction'] = metrics_off
            print(f"    ✓ Success: {metrics_off['draw_commands']} draw commands, "
                  f"{metrics_off['very_short_moves']} very short moves")
        else:
            print(f"    ✗ Failed")
            result['without_reduction'] = None
        
        # Test WITH noise reduction
        print(f"  Converting WITH noise reduction...")
        output_path_on = output_with_reduction / f'{name}.gcode'
        success, stdout, stderr = run_conversion(
            image_path, output_path_on,
            enable_noise_reduction=True,
            blur_kernel=5,
            morph_kernel=3,
            morph_iterations=1
        )
        
        if success and output_path_on.exists():
            metrics_on = analyze_gcode_quality(output_path_on)
            result['with_reduction'] = metrics_on
            print(f"    ✓ Success: {metrics_on['draw_commands']} draw commands, "
                  f"{metrics_on['very_short_moves']} very short moves")
        else:
            print(f"    ✗ Failed")
            result['with_reduction'] = None
        
        # Calculate improvements
        if result['without_reduction'] and result['with_reduction']:
            off = result['without_reduction']
            on = result['with_reduction']
            
            reduction_pct = ((off['draw_commands'] - on['draw_commands']) / off['draw_commands'] * 100) if off['draw_commands'] > 0 else 0
            short_reduction = off['very_short_moves'] - on['very_short_moves']
            
            result['improvement'] = {
                'commands_reduced': off['draw_commands'] - on['draw_commands'],
                'reduction_percentage': reduction_pct,
                'short_moves_eliminated': short_reduction
            }
            
            print(f"  📊 Improvement:")
            print(f"    • Commands reduced: {result['improvement']['commands_reduced']} ({reduction_pct:.1f}%)")
            print(f"    • Very short moves eliminated: {short_reduction}")
        
        results.append(result)
    
    # Generate summary report
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    total_reduction = 0
    total_short_eliminated = 0
    successful_tests = 0
    
    for result in results:
        if result.get('improvement'):
            successful_tests += 1
            total_reduction += result['improvement']['commands_reduced']
            total_short_eliminated += result['improvement']['short_moves_eliminated']
    
    print(f"\n✓ Tests completed: {len(results)}")
    print(f"✓ Successful comparisons: {successful_tests}")
    print(f"\n📊 Overall Impact:")
    print(f"  • Total commands eliminated: {total_reduction}")
    print(f"  • Total short moves eliminated: {total_short_eliminated}")
    print(f"  • Average reduction per image: {total_reduction / successful_tests:.0f} commands" if successful_tests > 0 else "")
    
    # Save results to JSON
    results_file = Path(__file__).parent.parent / 'test_data' / 'noise_reduction_test_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Detailed results saved to: {results_file}")
    
    # Print recommendations
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    print("""
For images with noise, compression artifacts, or dirty scans:
  
  BASIC (Mild noise):
    --enable-noise-reduction --gaussian-blur-kernel 3 --morph-kernel-size 2
  
  STANDARD (Moderate noise):
    --enable-noise-reduction --gaussian-blur-kernel 5 --morph-kernel-size 3
  
  AGGRESSIVE (Heavy noise):
    --enable-noise-reduction --gaussian-blur-kernel 7 --morph-kernel-size 4 --morph-iterations 2

Also consider increasing:
  --min-line-length 0.5    (Filter short segments)
  --simplify-epsilon 0.1   (Simplify curves)
    """)
    
    return results


if __name__ == '__main__':
    run_tests()
