#!/usr/bin/env python3
"""
Blueprint to G-code Converter
Converts blueprint-style images (black lines on white) to G-code for pen plotters.
"""

import argparse
import sys
from pathlib import Path
import numpy as np
from PIL import Image
import cv2
from scipy.spatial import distance_matrix
from scipy.optimize import linear_sum_assignment


class Blueprint2GCode:
    def __init__(self, args):
        self.input_path = args.input
        self.output_path = args.output
        self.z_up = args.z_up
        self.z_down = args.z_down
        self.feed_rate = args.feed_rate
        self.travel_rate = args.travel_rate
        self.margin = args.margin
        self.join_tolerance = args.join_tolerance
        self.min_line_length = args.min_line_length
        self.simplify_epsilon = args.simplify_epsilon
        
        # A4 dimensions in mm
        self.a4_width = 210
        self.a4_height = 297
        
    def load_and_preprocess_image(self):
        """Load image and convert to binary black/white."""
        print(f"Loading image: {self.input_path}")
        img = Image.open(self.input_path)
        
        # Convert to grayscale
        img_gray = img.convert('L')
        
        # Convert to numpy array (with explicit dtype for NumPy 2.0 compatibility)
        img_array = np.asarray(img_gray, dtype=np.uint8)
        
        # Threshold to binary (black lines on white background)
        # Using Otsu's method for automatic thresholding
        _, binary = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        print(f"Image size: {binary.shape[1]}x{binary.shape[0]} pixels")
        return binary, img_array.shape
    
    def detect_lines(self, binary_img):
        """Detect lines using skeletonization and contour detection."""
        print("Detecting lines...")
        
        # Skeletonize to get thin lines (no dilation to preserve parallel lines)
        skeleton = cv2.ximgproc.thinning(binary_img)
        
        # Find contours
        contours, _ = cv2.findContours(skeleton, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        print(f"Found {len(contours)} contours")
        
        # Convert contours to line segments
        lines = []
        for contour in contours:
            if len(contour) >= 2:
                perimeter = cv2.arcLength(contour, False)
                
                # Adaptive simplification: use less simplification for smaller contours
                # For very small contours (likely small text), use minimal simplification
                if perimeter < 30:  # Tiny features (fine text details)
                    epsilon = self.simplify_epsilon * 0.02 * perimeter  # 50x less simplification
                elif perimeter < 100:  # Small features (small text)
                    epsilon = self.simplify_epsilon * 0.08 * perimeter  # 12.5x less simplification
                elif perimeter < 300:  # Medium features
                    epsilon = self.simplify_epsilon * 0.2 * perimeter  # 5x less simplification
                else:
                    epsilon = self.simplify_epsilon * 0.5 * perimeter  # 2x less simplification
                
                # Ensure minimum epsilon to avoid too many points, but keep it very small
                epsilon = max(epsilon, 0.02)
                
                simplified = cv2.approxPolyDP(contour, epsilon, False)
                
                # Convert to list of points
                points = simplified.reshape(-1, 2).tolist()
                
                # Filter out very short lines
                if len(points) >= 2:
                    lines.append(points)
        
        print(f"Extracted {len(lines)} line segments")
        return lines
    
    def scale_to_a4(self, lines, img_shape):
        """Scale lines to fit A4 with margins."""
        img_height, img_width = img_shape
        
        # Calculate usable area
        usable_width = self.a4_width - 2 * self.margin
        usable_height = self.a4_height - 2 * self.margin
        
        # Determine orientation based on aspect ratio
        img_aspect = img_width / img_height
        a4_portrait_aspect = usable_width / usable_height
        a4_landscape_aspect = usable_height / usable_width
        
        # Choose orientation that better matches image
        if abs(img_aspect - a4_portrait_aspect) < abs(img_aspect - a4_landscape_aspect):
            # Portrait
            target_width = usable_width
            target_height = usable_height
            print(f"Using portrait orientation")
        else:
            # Landscape
            target_width = usable_height
            target_height = usable_width
            print(f"Using landscape orientation")
        
        # Calculate scale to fit within target area
        scale_x = target_width / img_width
        scale_y = target_height / img_height
        scale = min(scale_x, scale_y)
        
        # Calculate offsets to center the drawing
        scaled_width = img_width * scale
        scaled_height = img_height * scale
        offset_x = self.margin + (target_width - scaled_width) / 2
        offset_y = self.margin + (target_height - scaled_height) / 2
        
        print(f"Scale factor: {scale:.4f}")
        print(f"Output size: {scaled_width:.2f}x{scaled_height:.2f} mm")
        
        # Scale and translate all lines
        scaled_lines = []
        for line in lines:
            scaled_line = []
            for x, y in line:
                # Flip Y axis (image Y increases downward, plotter Y increases upward)
                new_x = x * scale + offset_x
                new_y = (img_height - y) * scale + offset_y
                scaled_line.append([new_x, new_y])
            scaled_lines.append(scaled_line)
        
        return scaled_lines
    
    def join_nearby_endpoints(self, lines):
        """Join line segments that have endpoints close together."""
        print("Joining nearby line endpoints...")
        
        # Build a graph of line segments
        joined = True
        iteration = 0
        
        while joined and iteration < 100:  # Limit iterations
            joined = False
            iteration += 1
            
            new_lines = []
            used = set()
            
            for i, line1 in enumerate(lines):
                if i in used:
                    continue
                
                # Try to extend this line
                extended = False
                for j, line2 in enumerate(lines):
                    if i == j or j in used:
                        continue
                    
                    # Check if endpoints are close
                    dist_end1_start2 = np.linalg.norm(np.array(line1[-1]) - np.array(line2[0]))
                    dist_end1_end2 = np.linalg.norm(np.array(line1[-1]) - np.array(line2[-1]))
                    dist_start1_start2 = np.linalg.norm(np.array(line1[0]) - np.array(line2[0]))
                    dist_start1_end2 = np.linalg.norm(np.array(line1[0]) - np.array(line2[-1]))
                    
                    if dist_end1_start2 < self.join_tolerance:
                        # Join line1 end to line2 start
                        new_lines.append(line1 + line2)
                        used.add(i)
                        used.add(j)
                        joined = True
                        extended = True
                        break
                    elif dist_end1_end2 < self.join_tolerance:
                        # Join line1 end to line2 end (reverse line2)
                        new_lines.append(line1 + line2[::-1])
                        used.add(i)
                        used.add(j)
                        joined = True
                        extended = True
                        break
                    elif dist_start1_start2 < self.join_tolerance:
                        # Join line1 start to line2 start (reverse line1)
                        new_lines.append(line1[::-1] + line2)
                        used.add(i)
                        used.add(j)
                        joined = True
                        extended = True
                        break
                    elif dist_start1_end2 < self.join_tolerance:
                        # Join line1 start to line2 end
                        new_lines.append(line2 + line1)
                        used.add(i)
                        used.add(j)
                        joined = True
                        extended = True
                        break
                
                if not extended:
                    new_lines.append(line1)
                    used.add(i)
            
            lines = new_lines
            if joined:
                print(f"  Iteration {iteration}: {len(lines)} line segments")
        
        # Filter out very short lines
        lines = [line for line in lines if self._line_length(line) >= self.min_line_length]
        
        print(f"After joining: {len(lines)} line segments")
        return lines
    
    def _line_length(self, line):
        """Calculate total length of a polyline."""
        length = 0
        for i in range(len(line) - 1):
            length += np.linalg.norm(np.array(line[i+1]) - np.array(line[i]))
        return length
    
    def optimize_path(self, lines):
        """Optimize drawing order to minimize pen travel."""
        if len(lines) <= 1:
            return lines
        
        print("Optimizing path...")
        
        # Use greedy nearest neighbor algorithm
        # Start from origin (0, 0)
        current_pos = [self.margin, self.margin]
        ordered_lines = []
        remaining = list(range(len(lines)))
        
        while remaining:
            # Find nearest line
            min_dist = float('inf')
            nearest_idx = -1
            reverse_nearest = False
            
            for idx in remaining:
                line = lines[idx]
                
                # Distance to start of line
                dist_start = np.linalg.norm(np.array(line[0]) - np.array(current_pos))
                # Distance to end of line (would draw in reverse)
                dist_end = np.linalg.norm(np.array(line[-1]) - np.array(current_pos))
                
                if dist_start < min_dist:
                    min_dist = dist_start
                    nearest_idx = idx
                    reverse_nearest = False
                
                if dist_end < min_dist:
                    min_dist = dist_end
                    nearest_idx = idx
                    reverse_nearest = True
            
            # Add nearest line to ordered list
            line = lines[nearest_idx]
            if reverse_nearest:
                line = line[::-1]
            
            ordered_lines.append(line)
            remaining.remove(nearest_idx)
            current_pos = line[-1]
            
            if len(ordered_lines) % 100 == 0:
                print(f"  Processed {len(ordered_lines)}/{len(lines)} lines")
        
        # Calculate total travel distance
        travel_dist = 0
        pos = [self.margin, self.margin]
        for line in ordered_lines:
            travel_dist += np.linalg.norm(np.array(line[0]) - np.array(pos))
            pos = line[-1]
        
        print(f"Total travel distance: {travel_dist:.2f} mm")
        return ordered_lines
    
    def generate_gcode(self, lines):
        """Generate G-code from optimized line paths."""
        print(f"Generating G-code: {self.output_path}")
        
        gcode = []
        
        # Header
        gcode.append("; Blueprint to G-code")
        gcode.append(f"; Input: {self.input_path}")
        gcode.append(f"; Generated with blueprint2gcode.py")
        gcode.append("")
        gcode.append("G21 ; Set units to millimeters")
        gcode.append("G90 ; Absolute positioning")
        gcode.append(f"G0 Z{self.z_up} ; Pen up")
        gcode.append("G0 X0 Y0 ; Move to origin")
        gcode.append("")
        
        # Draw lines
        total_draw_dist = 0
        total_travel_dist = 0
        current_pos = [0, 0]
        
        for i, line in enumerate(lines):
            # Move to start of line (pen up)
            travel_dist = np.linalg.norm(np.array(line[0]) - np.array(current_pos))
            total_travel_dist += travel_dist
            gcode.append(f"G0 X{line[0][0]:.3f} Y{line[0][1]:.3f} F{self.travel_rate} ; Travel to line {i+1}")
            
            # Pen down
            gcode.append(f"G0 Z{self.z_down} ; Pen down")
            
            # Draw line segments
            for point in line[1:]:
                draw_dist = np.linalg.norm(np.array(point) - np.array(current_pos))
                total_draw_dist += draw_dist
                gcode.append(f"G1 X{point[0]:.3f} Y{point[1]:.3f} F{self.feed_rate}")
                current_pos = point
            
            # Pen up
            gcode.append(f"G0 Z{self.z_up} ; Pen up")
            gcode.append("")
        
        # Footer
        gcode.append("; Return to origin")
        gcode.append("G0 X0 Y0")
        gcode.append(f"G0 Z{self.z_up}")
        gcode.append("")
        gcode.append(f"; Total drawing distance: {total_draw_dist:.2f} mm")
        gcode.append(f"; Total travel distance: {total_travel_dist:.2f} mm")
        gcode.append(f"; Total lines: {len(lines)}")
        est_time = (total_draw_dist / self.feed_rate + total_travel_dist / self.travel_rate) * 60
        gcode.append(f"; Estimated time: {est_time:.1f} seconds ({est_time/60:.1f} minutes)")
        gcode.append("M2 ; End program")
        
        # Write to file
        with open(self.output_path, 'w') as f:
            f.write('\n'.join(gcode))
        
        print(f"G-code generated successfully!")
        print(f"  Lines: {len(lines)}")
        print(f"  Drawing distance: {total_draw_dist:.2f} mm")
        print(f"  Travel distance: {total_travel_dist:.2f} mm")
        print(f"  Estimated time: {est_time/60:.1f} minutes")
    
    def convert(self):
        """Main conversion process."""
        # Load and preprocess image
        binary_img, img_shape = self.load_and_preprocess_image()
        
        # Detect lines
        lines = self.detect_lines(binary_img)
        
        if not lines:
            print("Error: No lines detected in image!")
            return False
        
        # Scale to A4
        lines = self.scale_to_a4(lines, img_shape)
        
        # Join nearby endpoints
        lines = self.join_nearby_endpoints(lines)
        
        # Optimize path
        lines = self.optimize_path(lines)
        
        # Generate G-code
        self.generate_gcode(lines)
        
        return True


def main():
    parser = argparse.ArgumentParser(
        description='Convert blueprint images to G-code for pen plotters',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument('input', type=str, help='Input image file (JPG or PNG)')
    parser.add_argument('output', type=str, help='Output G-code file')
    
    # Pen control
    parser.add_argument('--z-up', type=float, default=3.0,
                        help='Z position for pen up (mm)')
    parser.add_argument('--z-down', type=float, default=0.0,
                        help='Z position for pen down (mm)')
    
    # Feed rates
    parser.add_argument('--feed-rate', type=int, default=1000,
                        help='Drawing feed rate (mm/min)')
    parser.add_argument('--travel-rate', type=int, default=3000,
                        help='Travel feed rate when pen is up (mm/min)')
    
    # Output dimensions
    parser.add_argument('--margin', type=float, default=1.0,
                        help='Margin around A4 page (mm)')
    
    # Line processing
    parser.add_argument('--join-tolerance', type=float, default=0.15,
                        help='Maximum distance to join line endpoints (mm)')
    parser.add_argument('--min-line-length', type=float, default=0.3,
                        help='Minimum line length to include (mm)')
    parser.add_argument('--simplify-epsilon', type=float, default=0.0001,
                        help='Line simplification factor (lower = more detail)')
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        return 1
    
    # Create converter and run
    converter = Blueprint2GCode(args)
    success = converter.convert()
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
