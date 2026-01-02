#!/usr/bin/env python3
"""
Blueprint to G-code Converter
Converts blueprint-style images to G-code for pen plotters.
Supports both black-on-white and white-on-black images (use --invert-colors for the latter).
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
        self.paper_size = args.paper_size
        self.orientation = args.orientation
        self.fill_solid_areas = args.fill_solid_areas
        self.hatch_spacing = args.hatch_spacing
        self.hatch_angle = args.hatch_angle
        self.crosshatch = args.crosshatch
        self.min_solid_area = args.min_solid_area
        self.invert_colors = args.invert_colors
        
        # Paper dimensions in mm (width x height)
        self.paper_sizes = {
            'A3': (297, 420),
            'A4': (210, 297),
            'A5': (148, 210),
            'A6': (105, 148)
        }
        
        # Set paper dimensions based on selected size
        self.paper_width, self.paper_height = self.paper_sizes[self.paper_size]
        
        # Legacy compatibility
        self.a4_width = self.paper_width
        self.a4_height = self.paper_height
        
    def load_and_preprocess_image(self):
        """Load image and convert to binary black/white."""
        print(f"Loading image: {self.input_path}")
        img = Image.open(self.input_path)
        
        # Convert to grayscale
        img_gray = img.convert('L')
        
        # Convert to numpy array (with explicit dtype for NumPy 2.0 compatibility)
        img_array = np.asarray(img_gray, dtype=np.uint8)
        
        # Invert colors if requested (for white-on-black or white-on-blue images)
        if self.invert_colors:
            print("Inverting image colors...")
            img_array = 255 - img_array
        
        # Threshold to binary (black lines on white background)
        # Using Otsu's method for automatic thresholding
        _, binary = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        print(f"Image size: {binary.shape[1]}x{binary.shape[0]} pixels")
        return binary, img_array.shape
    
    def detect_solid_areas(self, binary_img):
        """Detect solid black areas (blobs) before skeletonization."""
        print("Detecting solid areas...")
        
        # Find all contours in the binary image
        # Use CHAIN_APPROX_NONE to preserve all points including sharp corners
        print("  Finding contours...")
        contours, hierarchy = cv2.findContours(binary_img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        print(f"  Found {len(contours)} contours, analyzing...")
        
        solid_areas = []
        parent_indices = set()  # Track which contours are parents of solid areas
        rejected_outline_parents = set()  # Track parents rejected as outlines
        
        if hierarchy is not None:
            hierarchy = hierarchy[0]
            
            for i, contour in enumerate(contours):
                # Calculate area
                area = cv2.contourArea(contour)
                
                # Only consider areas above minimum threshold
                if area < self.min_solid_area:
                    continue
                
                # Calculate solidity (ratio of contour area to convex hull area)
                hull = cv2.convexHull(contour)
                hull_area = cv2.contourArea(hull)
                
                if hull_area > 0:
                    solidity = area / hull_area
                    
                    # Check if this contour has any children (holes inside it)
                    has_children = hierarchy[i][2] != -1
                    is_child = hierarchy[i][3] != -1
                    
                    # Calculate perimeter to area ratio to distinguish walls from rooms
                    perimeter = cv2.arcLength(contour, True)
                    compactness = (perimeter * perimeter) / area if area > 0 else float('inf')
                    
                    # Calculate average thickness to distinguish outlines from solid areas
                    # Thickness = area / perimeter gives approximate "width" of the shape
                    # Thin outlines (like circle strokes) will have low thickness
                    # Solid filled shapes will have higher thickness
                    thickness = area / perimeter if perimeter > 0 else 0
                    min_thickness = 10  # Minimum thickness in pixels to be considered solid
                    
                    # Filled solid shapes can be:
                    # 1. Outer contours with high solidity and no children (truly solid blobs)
                    # 2. Outer contours with children (solid area with holes) - but NOT the children themselves
                    # 3. Child contours in floor plans where walls are separate filled rectangles
                    # 4. Shapes with reasonable compactness (not extremely elongated or hollow)
                    # 5. Must have sufficient thickness (not just thin outlines)
                    
                    is_solid = False
                    
                    # For parent contours with children (holes), lower the solidity threshold
                    # because holes reduce the solidity ratio
                    if has_children and not is_child:
                        # Parent with holes - need to distinguish between:
                        # - Solid shapes with holes (mechanical part): high fill ratio and sufficient thickness
                        # - Outline shapes (circles/squares strokes): thin, mostly hollow
                        
                        # Calculate what percentage is actually filled (not holes)
                        # by checking the children's total area
                        children_area = 0
                        child_idx = hierarchy[i][2]  # First child
                        while child_idx != -1:
                            children_area += cv2.contourArea(contours[child_idx])
                            child_idx = hierarchy[child_idx][0]  # Next sibling
                        
                        fill_ratio = (area - children_area) / area if area > 0 else 0
                        
                        # Only accept if:
                        # 1. Reasonable compactness (not huge outline)
                        # 2. Sufficient fill ratio to exclude outline strokes
                        #    - Outline strokes: < 0.05 (5% filled - thin ring)
                        #    - Floor plans: 0.15-0.45 (15-45% filled - walls + rooms)
                        #    - Solid with holes: > 0.85 (85% filled - mostly solid)
                        # 3. Sufficient thickness (not a thin outline stroke)
                        if solidity > 0.5 and compactness < 200 and fill_ratio > 0.15 and thickness >= min_thickness:
                            is_solid = True
                            parent_indices.add(i)  # Mark this as a parent
                        else:
                            # Mark as rejected outline parent so we skip its children
                            rejected_outline_parents.add(i)
                    elif solidity > 0.7 and thickness >= min_thickness:
                        if not has_children and not is_child:
                            # Truly solid shape with no holes
                            is_solid = True
                        elif is_child:
                            # Check if this child's parent is already marked as solid
                            parent_idx = hierarchy[i][3]
                            if parent_idx in rejected_outline_parents:
                                # Parent was rejected as an outline, so this child is just
                                # the interior space (not a solid area to fill)
                                pass
                            elif parent_idx not in parent_indices:
                                # Parent is not solid, so this might be a standalone filled child
                                # (like floor plan walls)
                                if solidity > 0.95 and compactness < 50:
                                    is_solid = True
                            # else: parent is solid, so don't fill the holes
                        elif not has_children and compactness < 100:
                            # Single contour with moderate compactness
                            is_solid = True
                    
                    if is_solid:
                        # Store contour index so we can find its children later
                        solid_areas.append((i, contour))
        
        print(f"Found {len(solid_areas)} solid areas")
        
        # Return both the solid areas and the hierarchy info
        return solid_areas, hierarchy, contours
    
    def generate_hatch_lines(self, contour_info, img_shape, hierarchy=None, all_contours=None):
        """Generate hatching lines for a solid area, excluding any holes (child contours)."""
        # Handle both old format (just contour) and new format (index, contour)
        if isinstance(contour_info, tuple):
            contour_idx, contour = contour_info
        else:
            contour_idx = None
            contour = contour_info
        # Get bounding box
        x, y, w, h = cv2.boundingRect(contour)
        
        # Create a mask for this contour
        mask = np.zeros(img_shape, dtype=np.uint8)
        cv2.drawContours(mask, [contour], -1, 255, -1)
        
        # If this contour has children (holes), subtract them from the mask
        if contour_idx is not None and hierarchy is not None and all_contours is not None:
            child_idx = hierarchy[contour_idx][2]  # First child
            while child_idx != -1:
                # Draw child contour as black (0) to create holes in the mask
                cv2.drawContours(mask, [all_contours[child_idx]], -1, 0, -1)
                child_idx = hierarchy[child_idx][0]  # Next sibling
        
        hatch_lines = []
        
        # Convert angle to radians
        angle_rad = np.deg2rad(self.hatch_angle)
        
        # Calculate perpendicular direction (normal to hatch lines)
        perp_angle = angle_rad + np.pi/2
        dx_perp = np.cos(perp_angle)
        dy_perp = np.sin(perp_angle)
        
        # Calculate line direction (along hatch lines)
        dx_line = np.cos(angle_rad)
        dy_line = np.sin(angle_rad)
        
        # Calculate how far we need to extend to cover the bounding box
        # Use the diagonal plus extra margin to ensure we reach all corners
        diagonal = int(np.sqrt(w**2 + h**2)) + 20
        
        # Center of bounding box
        cx, cy = x + w/2, y + h/2
        
        # Use hatch_spacing_pixels instead of hatch_spacing
        hatch_spacing_px = getattr(self, 'hatch_spacing_pixels', self.hatch_spacing)
        
        # Calculate the perpendicular extent needed to cover all corners
        # Project all 4 corners onto the perpendicular axis to find the range
        corners = [
            (x, y), (x + w, y), (x, y + h), (x + w, y + h)
        ]
        perp_offsets = []
        for corner_x, corner_y in corners:
            # Perpendicular offset from center to this corner
            offset = (corner_x - cx) * dx_perp + (corner_y - cy) * dy_perp
            perp_offsets.append(offset)
        
        # Extend beyond the min/max corners to ensure complete coverage
        min_offset = min(perp_offsets) - hatch_spacing_px * 2
        max_offset = max(perp_offsets) + hatch_spacing_px * 2
        
        # Generate lines from min to max offset at regular spacing
        num_lines = int((max_offset - min_offset) / hatch_spacing_px) + 3
        
        # Add explicit lines through each corner to ensure they're covered
        # For corners that diagonal lines barely touch, add multiple nearby lines
        corner_line_offsets = set()
        for corner_x, corner_y in corners:
            corner_offset = (corner_x - cx) * dx_perp + (corner_y - cy) * dy_perp
            # Add the exact corner line
            corner_line_offsets.add(corner_offset)
            # Add a few lines on either side of the corner (sub-spacing intervals)
            for delta in [-0.8, -0.4, 0.4, 0.8]:
                corner_line_offsets.add(corner_offset + delta)
        
        # Merge regular offsets with corner offsets
        all_offsets = []
        for i in range(num_lines):
            regular_offset = min_offset + i * hatch_spacing_px
            all_offsets.append(regular_offset)
        
        # Add corner offsets if they're not already close to a regular offset
        for corner_offset in corner_line_offsets:
            # Check if any regular offset is within  a tiny tolerance of this corner
            # Use very small tolerance to ensure we actually generate lines AT corners
            has_nearby = any(abs(corner_offset - reg_offset) < 0.1 
                           for reg_offset in all_offsets)
            if not has_nearby:
                all_offsets.append(corner_offset)
        
        # Sort for orderly processing
        all_offsets.sort()
        
        for offset in all_offsets:
            
            # Start point of this hatch line (far to one side along line direction)
            px = cx + offset * dx_perp - diagonal * dx_line
            py = cy + offset * dy_perp - diagonal * dy_line
            
            # End point of this hatch line (far to other side along line direction)
            qx = cx + offset * dx_perp + diagonal * dx_line
            qy = cy + offset * dy_perp + diagonal * dy_line
            
            # Convert to integer coordinates
            p1 = (int(round(px)), int(round(py)))
            p2 = (int(round(qx)), int(round(qy)))
            
            # Clip to image bounds
            p1 = (max(0, min(img_shape[1]-1, p1[0])), max(0, min(img_shape[0]-1, p1[1])))
            p2 = (max(0, min(img_shape[1]-1, p2[0])), max(0, min(img_shape[0]-1, p2[1])))
            
            # GEOMETRIC APPROACH: Scan along the line and find all intersection segments
            # This avoids rasterization issues at corners where cv2.line only hits 1-2 pixels
            
            # Line parametric form: point = p1 + t * direction, where t goes from 0 to 1
            line_start = np.array([float(p1[0]), float(p1[1])])
            line_end = np.array([float(p2[0]), float(p2[1])])
            line_vec = line_end - line_start
            line_length = np.linalg.norm(line_vec)
            
            if line_length < 1:
                continue
            
            line_dir = line_vec / line_length
            
            # Sample along the line at very dense sub-pixel intervals to catch corner pixels
            # Use 10 samples per pixel to ensure we don't miss single-pixel corner touches
            num_samples = int(line_length * 10) + 20
            
            intersections = []
            in_mask = False
            segment_start = None
            
            for sample_idx in range(num_samples):
                t = sample_idx / (num_samples - 1)
                point = line_start + t * line_vec
                
                x, y = int(round(point[0])), int(round(point[1]))
                
                # Check bounds
                if x < 0 or x >= img_shape[1] or y < 0 or y >= img_shape[0]:
                    if in_mask and segment_start is not None:
                        # Exited bounds while in mask - close segment at boundary
                        intersections.append((segment_start, point))
                        in_mask = False
                        segment_start = None
                    continue
                
                # Check if this point is in the mask
                is_in_mask = mask[y, x] > 0
                
                if is_in_mask and not in_mask:
                    # Entering mask - start new segment
                    segment_start = point.copy()
                    in_mask = True
                elif not is_in_mask and in_mask:
                    # Leaving mask - close current segment
                    if segment_start is not None:
                        intersections.append((segment_start, point))
                    in_mask = False
                    segment_start = None
            
            # Close any open segment at the end
            if in_mask and segment_start is not None:
                intersections.append((segment_start, line_end))
            
            # Now extend each intersection segment to the actual mask boundaries
            # using precise ray marching in the hatch direction
            hatch_dir = np.array([dx_line, dy_line])
            
            def extend_to_boundary_precise(start_pos, direction, mask, max_steps=1000):
                """Extend from start position along direction until leaving mask.
                Returns the furthest point still inside the mask."""
                pos = start_pos.copy()
                step_size = 0.2  # Sub-pixel steps
                last_valid = pos.copy()
                
                for _ in range(max_steps):
                    pos = pos + direction * step_size
                    x, y = int(round(pos[0])), int(round(pos[1]))
                    
                    # Check bounds
                    if x < 0 or x >= mask.shape[1] or y < 0 or y >= mask.shape[0]:
                        return last_valid
                    
                    # Check mask
                    if mask[y, x] > 0:
                        last_valid = pos.copy()
                    else:
                        # Left the mask
                        return last_valid
                
                return last_valid
            
            # Process each intersection segment
            for seg_start, seg_end in intersections:
                # Extend both ends to mask boundaries using the hatch direction
                extended_start = extend_to_boundary_precise(seg_start, -hatch_dir, mask)
                extended_end = extend_to_boundary_precise(seg_end, hatch_dir, mask)
                
                # Only add if the segment has reasonable length
                seg_length = np.linalg.norm(extended_end - extended_start)
                if seg_length > 0.5:  # At least half a pixel
                    hatch_lines.append([
                        [int(round(extended_start[0])), int(round(extended_start[1]))],
                        [int(round(extended_end[0])), int(round(extended_end[1]))]
                    ])
        
        # Add extra lines near corners to improve coverage for diagonal hatching
        # For 45° hatching, some corners are geometrically hard to reach with regular spacing
        if len(hatch_lines) > 0 and abs(self.hatch_angle % 90) > 5:
            # Find mask extremes
            mask_points = np.argwhere(mask > 0)
            if len(mask_points) > 0:
                min_y, min_x = mask_points.min(axis=0)
                max_y, max_x = mask_points.max(axis=0)
                
                # Define corner regions (10% of dimensions)
                corner_margin = int(min(max_x - min_x, max_y - min_y) * 0.1)
                
                # For each corner, generate additional lines with tighter spacing
                corners = [
                    (min_x, min_y),  # Top-left
                    (max_x, min_y),  # Top-right
                    (min_x, max_y),  # Bottom-left
                    (max_x, max_y),  # Bottom-right
                ]
                
                # Use half the normal spacing for corner fill
                corner_spacing = hatch_spacing_px / 2.0
                
                for corner_x, corner_y in corners:
                    # Calculate perpendicular offset for this corner
                    vx, vy = corner_x - cx, corner_y - cy
                    corner_offset = vx * dx_perp + vy * dy_perp
                    
                    # Generate 3-5 extra lines around this corner's offset
                    for extra in range(-2, 3):
                        offset = corner_offset + extra * corner_spacing
                        
                        # Generate line at this offset
                        px = cx + offset * dx_perp - diagonal * dx_line
                        py = cy + offset * dy_perp - diagonal * dy_line
                        qx = cx + offset * dx_perp + diagonal * dx_line
                        qy = cy + offset * dy_perp + diagonal * dy_line
                        
                        p1_corner = (int(round(px)), int(round(py)))
                        p2_corner = (int(round(qx)), int(round(qy)))
                        
                        # Clip to bounds
                        p1_corner = (max(0, min(img_shape[1]-1, p1_corner[0])), 
                                   max(0, min(img_shape[0]-1, p1_corner[1])))
                        p2_corner = (max(0, min(img_shape[1]-1, p2_corner[0])), 
                                   max(0, min(img_shape[0]-1, p2_corner[1])))
                        
                        # Sample and find intersections (same as above)
                        line_start = np.array([float(p1_corner[0]), float(p1_corner[1])])
                        line_end = np.array([float(p2_corner[0]), float(p2_corner[1])])
                        line_vec = line_end - line_start
                        line_length = np.linalg.norm(line_vec)
                        
                        if line_length < 1:
                            continue
                        
                        line_dir = line_vec / line_length
                        num_samples = int(line_length * 2) + 10
                        
                        intersections = []
                        in_mask = False
                        segment_start = None
                        
                        for sample_idx in range(num_samples):
                            t = sample_idx / (num_samples - 1)
                            point = line_start + t * line_vec
                            
                            x, y = int(round(point[0])), int(round(point[1]))
                            
                            if x < 0 or x >= img_shape[1] or y < 0 or y >= img_shape[0]:
                                if in_mask and segment_start is not None:
                                    intersections.append((segment_start, point))
                                    in_mask = False
                                    segment_start = None
                                continue
                            
                            is_in_mask = mask[y, x] > 0
                            
                            if is_in_mask and not in_mask:
                                segment_start = point.copy()
                                in_mask = True
                            elif not is_in_mask and in_mask:
                                if segment_start is not None:
                                    intersections.append((segment_start, point))
                                in_mask = False
                                segment_start = None
                        
                        if in_mask and segment_start is not None:
                            intersections.append((segment_start, line_end))
                        
                        # Add segments (only if they're in the corner region)
                        for seg_start, seg_end in intersections:
                            # Check if this segment is actually near the corner
                            seg_center = (seg_start + seg_end) / 2
                            if (abs(seg_center[0] - corner_x) < corner_margin and 
                                abs(seg_center[1] - corner_y) < corner_margin):
                                
                                hatch_dir = np.array([dx_line, dy_line])
                                extended_start = extend_to_boundary_precise(seg_start, -hatch_dir, mask)
                                extended_end = extend_to_boundary_precise(seg_end, hatch_dir, mask)
                                
                                seg_length = np.linalg.norm(extended_end - extended_start)
                                if seg_length > 0.5:
                                    hatch_lines.append([
                                        [int(round(extended_start[0])), int(round(extended_start[1]))],
                                        [int(round(extended_end[0])), int(round(extended_end[1]))]
                                    ])
        
        return hatch_lines
    
    def detect_lines(self, binary_img):
        """Detect lines using skeletonization and contour detection."""
        print("Detecting lines...")
        
        # Detect and handle solid areas if enabled
        solid_lines = []
        if self.fill_solid_areas:
            solid_areas, hierarchy, all_contours = self.detect_solid_areas(binary_img)
            
            # Create a mask to remove solid areas from line detection
            mask_for_lines = binary_img.copy()
            for contour_info in solid_areas:
                # Handle both tuple and contour formats
                contour = contour_info[1] if isinstance(contour_info, tuple) else contour_info
                cv2.drawContours(mask_for_lines, [contour], -1, 0, -1)
            
            # Generate hatch lines for solid areas
            if getattr(self, 'crosshatch', False):
                # Crosshatch mode: generate two perpendicular sets of lines
                print(f"  Generating crosshatch lines for {len(solid_areas)} solid areas...")
                print(f"    Pass 1: {self.hatch_angle}° hatching...")
                for idx, contour_info in enumerate(solid_areas):
                    if (idx + 1) % 5 == 0 or idx == 0:
                        print(f"      Processing area {idx + 1}/{len(solid_areas)}...")
                    hatch_lines = self.generate_hatch_lines(contour_info, binary_img.shape, hierarchy, all_contours)
                    solid_lines.extend(hatch_lines)
                
                pass1_count = len(solid_lines)
                print(f"    Pass 1 complete: {pass1_count} lines")
                
                # Second pass with perpendicular angle
                perpendicular_angle = self.hatch_angle + 90
                original_angle = self.hatch_angle
                self.hatch_angle = perpendicular_angle
                
                print(f"    Pass 2: {self.hatch_angle}° hatching...")
                for idx, contour_info in enumerate(solid_areas):
                    if (idx + 1) % 5 == 0 or idx == 0:
                        print(f"      Processing area {idx + 1}/{len(solid_areas)}...")
                    hatch_lines = self.generate_hatch_lines(contour_info, binary_img.shape, hierarchy, all_contours)
                    solid_lines.extend(hatch_lines)
                
                # Restore original angle
                self.hatch_angle = original_angle
                
                pass2_count = len(solid_lines) - pass1_count
                print(f"    Pass 2 complete: {pass2_count} lines")
                print(f"Generated {len(solid_lines)} total crosshatch lines for solid areas")
            else:
                # Single-angle mode: faster but may miss some sharp corners
                print(f"  Generating hatch lines for {len(solid_areas)} solid areas...")
                for idx, contour_info in enumerate(solid_areas):
                    if (idx + 1) % 5 == 0 or idx == 0:
                        print(f"    Processing area {idx + 1}/{len(solid_areas)}...")
                    hatch_lines = self.generate_hatch_lines(contour_info, binary_img.shape, hierarchy, all_contours)
                    solid_lines.extend(hatch_lines)
                
                print(f"Generated {len(solid_lines)} hatch lines for solid areas")
            
            # Use masked image for line detection
            binary_for_lines = mask_for_lines
        else:
            binary_for_lines = binary_img
        
        # Skeletonize to get thin lines (no dilation to preserve parallel lines)
        print("  Skeletonizing image...")
        skeleton = cv2.ximgproc.thinning(binary_for_lines)
        
        # Find contours
        print("  Finding line contours...")
        contours, _ = cv2.findContours(skeleton, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        print(f"Found {len(contours)} contours")
        
        # Convert contours to line segments
        lines = []
        for contour in contours:
            if len(contour) >= 2:
                perimeter = cv2.arcLength(contour, False)
                
                # Adaptive simplification: use less simplification for smaller contours
                # For very small contours (likely small text), use minimal simplification
                if perimeter < 30:  # Tiny features (fine text details, punctuation, arrows)
                    epsilon = self.simplify_epsilon * 0.001 * perimeter  # 1000x less simplification
                elif perimeter < 100:  # Small features (small text)
                    epsilon = self.simplify_epsilon * 0.005 * perimeter  # 200x less simplification
                elif perimeter < 300:  # Medium features
                    epsilon = self.simplify_epsilon * 0.02 * perimeter  # 50x less simplification
                else:
                    epsilon = self.simplify_epsilon * 0.1 * perimeter  # 10x less simplification
                
                # Ensure minimum epsilon to avoid too many points, but keep it very small for detail
                epsilon = max(epsilon, 0.001)
                
                simplified = cv2.approxPolyDP(contour, epsilon, False)
                
                # Convert to list of points
                points = simplified.reshape(-1, 2).tolist()
                
                # Filter out very short lines
                if len(points) >= 2:
                    lines.append(points)
        
        # Add solid area hatch lines
        lines.extend(solid_lines)
        
        print(f"Extracted {len(lines)} line segments (including {len(solid_lines)} hatch lines)")
        return lines
    
    def scale_to_a4(self, lines, img_shape):
        """Scale lines to fit paper size with margins."""
        img_height, img_width = img_shape
        
        # Calculate usable area
        usable_width = self.paper_width - 2 * self.margin
        usable_height = self.paper_height - 2 * self.margin
        
        # Determine if we need to rotate based on orientation preference
        img_aspect = img_width / img_height
        portrait_aspect = usable_width / usable_height
        landscape_aspect = usable_height / usable_width
        
        # Determine desired orientation
        if self.orientation == 'auto':
            # Choose orientation that better matches image
            if abs(img_aspect - portrait_aspect) < abs(img_aspect - landscape_aspect):
                use_portrait = True
            else:
                use_portrait = False
        elif self.orientation == 'portrait':
            use_portrait = True
        else:  # landscape
            use_portrait = False
        
        # Check if we need to rotate the image (swap dimensions)
        # For square images, no rotation is needed
        if img_width == img_height:
            need_rotation = False
        else:
            img_is_portrait = img_width < img_height
            need_rotation = (use_portrait and not img_is_portrait) or (not use_portrait and img_is_portrait)
        
        if need_rotation:
            print(f"Rotating image 90° to match {self.orientation} orientation")
            # Rotate lines by 90 degrees and swap dimensions
            rotated_lines = []
            for line in lines:
                rotated_line = []
                for x, y in line:
                    # Rotate 90° clockwise: (x, y) -> (height - y, x)
                    new_x = img_height - y
                    new_y = x
                    rotated_line.append([new_x, new_y])
                rotated_lines.append(rotated_line)
            lines = rotated_lines
            # Swap dimensions
            img_width, img_height = img_height, img_width
        
        # Set target dimensions based on orientation
        if use_portrait:
            target_width = usable_width
            target_height = usable_height
            print(f"Using portrait orientation ({self.paper_size})")
        else:
            target_width = usable_height
            target_height = usable_width
            print(f"Using landscape orientation ({self.paper_size})")
        
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
        print(f"Joining nearby line endpoints... (starting with {len(lines)} segments)")
        
        # Build a graph of line segments
        joined = True
        iteration = 0
        
        while joined and iteration < 100:  # Limit iterations
            joined = False
            iteration += 1
            if iteration == 1:
                print(f"  Processing iteration {iteration}... (this may take a moment for large files)")
            
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
        
        print(f"Optimizing path for {len(lines)} line segments...")
        
        # Use greedy nearest neighbor algorithm
        # Start from origin (0, 0)
        current_pos = [self.margin, self.margin]
        ordered_lines = []
        remaining = list(range(len(lines)))
        
        if len(lines) > 500:
            print("  This may take a minute for large files...")
        
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
            
            # Show progress more frequently for better feedback
            if len(ordered_lines) % 50 == 0:
                percent = (len(ordered_lines) / len(lines)) * 100
                print(f"  Processed {len(ordered_lines)}/{len(lines)} lines ({percent:.1f}%)")
        
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
        
        # Calculate scale factor for pixel-to-mm conversion (needed for hatch spacing)
        img_height, img_width = img_shape
        usable_width = self.paper_width - (2 * self.margin)
        usable_height = self.paper_height - (2 * self.margin)
        
        # Determine orientation
        if self.orientation == 'auto':
            img_is_portrait = img_width < img_height
            use_portrait = img_is_portrait
        else:
            use_portrait = (self.orientation == 'portrait')
        
        # Set target dimensions based on orientation
        if use_portrait:
            target_width = usable_width
            target_height = usable_height
        else:
            target_width = usable_height
            target_height = usable_width
        
        # Calculate scale (pixels -> mm)
        scale_x = target_width / img_width
        scale_y = target_height / img_height
        self.pixels_to_mm_scale = min(scale_x, scale_y)
        
        print(f"Pixels to mm scale: {self.pixels_to_mm_scale:.4f}")
        
        # Convert hatch spacing from mm to pixels for line detection
        self.hatch_spacing_pixels = self.hatch_spacing / self.pixels_to_mm_scale
        print(f"Hatch spacing: {self.hatch_spacing}mm = {self.hatch_spacing_pixels:.2f}px")
        
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
    parser.add_argument('--paper-size', type=str, default='A4',
                        choices=['A3', 'A4', 'A5', 'A6'],
                        help='Output paper size')
    parser.add_argument('--orientation', type=str, default='auto',
                        choices=['auto', 'portrait', 'landscape'],
                        help='Output orientation (auto, portrait, or landscape)')
    parser.add_argument('--margin', type=float, default=1.0,
                        help='Margin around page (mm)')
    
    # Line processing
    parser.add_argument('--join-tolerance', type=float, default=0.02,
                        help='Maximum distance to join line endpoints (mm)')
    parser.add_argument('--min-line-length', type=float, default=0.01,
                        help='Minimum line length to include (mm)')
    parser.add_argument('--simplify-epsilon', type=float, default=0.000001,
                        help='Line simplification factor (lower = more detail)')
    
    # Solid area filling
    parser.add_argument('--fill-solid-areas', action='store_true',
                        help='Fill solid black areas with hatching instead of outlining')
    parser.add_argument('--hatch-spacing', type=float, default=1.0,
                        help='Spacing between hatch lines in pixels (before scaling)')
    parser.add_argument('--hatch-angle', type=float, default=45.0,
                        help='Angle of hatch lines in degrees')
    parser.add_argument('--crosshatch', action='store_true',
                        help='Use crosshatch pattern (two perpendicular angles) for complete corner coverage')
    parser.add_argument('--min-solid-area', type=float, default=100.0,
                        help='Minimum area in pixels to consider as solid (before scaling)')
    
    # Image preprocessing
    parser.add_argument('--invert-colors', action='store_true',
                        help='Invert image colors before processing (useful for white-on-black or white-on-blue images)')
    
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
