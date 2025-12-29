#!/usr/bin/env python3
"""
Generate sample blueprint-style test images
"""

import numpy as np
from PIL import Image, ImageDraw
import math


def create_test_image_1_simple_box():
    """Simple rectangle with diagonal"""
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Rectangle
    draw.rectangle([100, 100, 700, 500], outline='black', width=3)
    
    # Diagonal
    draw.line([100, 100, 700, 500], fill='black', width=3)
    
    # Cross in center
    draw.line([400, 200, 400, 400], fill='black', width=2)
    draw.line([300, 300, 500, 300], fill='black', width=2)
    
    img.save('test_images/test1_simple_box.png')
    print("Created test1_simple_box.png")


def create_test_image_2_floor_plan():
    """Simple floor plan style"""
    img = Image.new('RGB', (1000, 800), color='white')
    draw = ImageDraw.Draw(img)
    
    # Outer walls
    draw.rectangle([50, 50, 950, 750], outline='black', width=4)
    
    # Interior walls
    draw.line([500, 50, 500, 750], fill='black', width=4)
    draw.line([50, 400, 950, 400], fill='black', width=4)
    
    # Doors (gaps will be separate lines)
    draw.line([200, 50, 200, 100], fill='black', width=2)
    draw.line([200, 150, 200, 400], fill='black', width=2)
    
    draw.line([700, 50, 700, 100], fill='black', width=2)
    draw.line([700, 150, 700, 400], fill='black', width=2)
    
    # Windows
    draw.rectangle([150, 45, 250, 55], outline='black', width=2)
    draw.rectangle([650, 45, 750, 55], outline='black', width=2)
    
    # Stairs
    for i in range(10):
        y = 450 + i * 25
        draw.line([100, y, 200, y], fill='black', width=2)
    
    img.save('test_images/test2_floor_plan.png')
    print("Created test2_floor_plan.png")


def create_test_image_3_geometric():
    """Geometric shapes"""
    img = Image.new('RGB', (800, 800), color='white')
    draw = ImageDraw.Draw(img)
    
    # Circle
    draw.ellipse([50, 50, 250, 250], outline='black', width=3)
    
    # Triangle
    draw.polygon([600, 50, 750, 250, 450, 250], outline='black', width=3)
    
    # Hexagon
    cx, cy, r = 400, 500, 150
    points = []
    for i in range(6):
        angle = math.pi / 3 * i
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append((x, y))
    draw.polygon(points, outline='black', width=3)
    
    # Star
    cx, cy, r1, r2 = 150, 550, 80, 40
    star_points = []
    for i in range(10):
        angle = math.pi / 5 * i - math.pi / 2
        r = r1 if i % 2 == 0 else r2
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        star_points.append((x, y))
    draw.polygon(star_points, outline='black', width=3)
    
    # Spiral
    cx, cy = 650, 550
    points = []
    for i in range(100):
        angle = i * 0.3
        r = 5 + i * 0.8
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append((x, y))
    draw.line(points, fill='black', width=2)
    
    img.save('test_images/test3_geometric.png')
    print("Created test3_geometric.png")


def create_test_image_4_mechanical():
    """Mechanical drawing style"""
    img = Image.new('RGB', (1000, 700), color='white')
    draw = ImageDraw.Draw(img)
    
    # Main part outline
    draw.rectangle([200, 200, 800, 500], outline='black', width=3)
    
    # Mounting holes
    holes = [(300, 300), (700, 300), (300, 400), (700, 400)]
    for x, y in holes:
        draw.ellipse([x-30, y-30, x+30, y+30], outline='black', width=2)
        # Cross hair
        draw.line([x-40, y, x+40, y], fill='black', width=1)
        draw.line([x, y-40, x, y+40], fill='black', width=1)
    
    # Center circle
    draw.ellipse([450, 300, 550, 400], outline='black', width=3)
    
    # Dimension lines
    draw.line([200, 150, 800, 150], fill='black', width=1)
    draw.line([200, 140, 200, 160], fill='black', width=1)
    draw.line([800, 140, 800, 160], fill='black', width=1)
    
    draw.line([150, 200, 150, 500], fill='black', width=1)
    draw.line([140, 200, 160, 200], fill='black', width=1)
    draw.line([140, 500, 160, 500], fill='black', width=1)
    
    # Hidden lines (dashed)
    for i in range(0, 600, 30):
        draw.line([200 + i, 350, 200 + i + 15, 350], fill='black', width=1)
    
    img.save('test_images/test4_mechanical.png')
    print("Created test4_mechanical.png")


def create_test_image_5_circuit():
    """Circuit diagram style"""
    img = Image.new('RGB', (900, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Resistor
    x, y = 100, 200
    draw.line([x, y, x+40, y], fill='black', width=2)
    draw.rectangle([x+40, y-15, x+120, y+15], outline='black', width=2)
    draw.line([x+120, y, x+160, y], fill='black', width=2)
    
    # Capacitor
    x, y = 100, 350
    draw.line([x, y, x+70, y], fill='black', width=2)
    draw.line([x+70, y-20, x+70, y+20], fill='black', width=3)
    draw.line([x+90, y-20, x+90, y+20], fill='black', width=3)
    draw.line([x+90, y, x+160, y], fill='black', width=2)
    
    # Connection lines
    draw.line([160, 200, 300, 200], fill='black', width=2)
    draw.line([300, 200, 300, 300], fill='black', width=2)
    draw.line([160, 350, 300, 350], fill='black', width=2)
    draw.line([300, 350, 300, 300], fill='black', width=2)
    
    # IC chip
    x, y = 400, 250
    draw.rectangle([x, y, x+120, y+100], outline='black', width=3)
    # Pins
    for i in range(4):
        pin_y = y + 20 + i * 25
        draw.line([x, pin_y, x-20, pin_y], fill='black', width=2)
        draw.line([x+120, pin_y, x+140, pin_y], fill='black', width=2)
    
    # Ground symbol
    x, y = 300, 400
    draw.line([x, 350, x, y], fill='black', width=2)
    draw.line([x-30, y, x+30, y], fill='black', width=3)
    draw.line([x-20, y+10, x+20, y+10], fill='black', width=2)
    draw.line([x-10, y+20, x+10, y+20], fill='black', width=2)
    
    # LED
    x, y = 650, 300
    draw.polygon([x, y-20, x, y+20, x+30, y], outline='black', width=2)
    draw.line([x+30, y-20, x+30, y+20], fill='black', width=2)
    draw.line([x-30, y, x, y], fill='black', width=2)
    draw.line([x+30, y, x+60, y], fill='black', width=2)
    
    # Arrows for LED
    draw.line([x+10, y-25, x+20, y-35], fill='black', width=1)
    draw.polygon([x+20, y-35, x+15, y-33, x+18, y-30], fill='black')
    
    img.save('test_images/test5_circuit.png')
    print("Created test5_circuit.png")


def create_test_image_6_text_labels():
    """Technical drawing with text labels and annotations"""
    img = Image.new('RGB', (1000, 800), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use different font sizes (will use default if fonts not available)
    try:
        from PIL import ImageFont
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        # Fallback to default font
        font_large = None
        font_medium = None
        font_small = None
        font_tiny = None
    
    # Title block
    draw.rectangle([50, 50, 950, 150], outline='black', width=3)
    draw.line([50, 100, 950, 100], fill='black', width=2)
    draw.line([500, 50, 500, 150], fill='black', width=2)
    
    # Title text
    draw.text((80, 65), "ASSEMBLY DRAWING", fill='black', font=font_large)
    draw.text((520, 70), "SCALE: 1:10", fill='black', font=font_medium)
    draw.text((520, 110), "DATE: 2025-12-28", fill='black', font=font_small)
    
    # Main part with dimensions
    part_x, part_y = 200, 300
    part_w, part_h = 600, 250
    draw.rectangle([part_x, part_y, part_x+part_w, part_y+part_h], outline='black', width=4)
    
    # Dimension lines with text
    # Horizontal dimension
    dim_y = part_y - 60
    draw.line([part_x, dim_y, part_x+part_w, dim_y], fill='black', width=2)
    draw.line([part_x, dim_y-10, part_x, dim_y+10], fill='black', width=2)
    draw.line([part_x+part_w, dim_y-10, part_x+part_w, dim_y+10], fill='black', width=2)
    # Arrow heads
    draw.polygon([part_x+10, dim_y, part_x, dim_y-5, part_x, dim_y+5], fill='black')
    draw.polygon([part_x+part_w-10, dim_y, part_x+part_w, dim_y-5, part_x+part_w, dim_y+5], fill='black')
    draw.text((part_x + part_w/2 - 40, dim_y - 35), "600mm", fill='black', font=font_medium)
    
    # Vertical dimension
    dim_x = part_x - 60
    draw.line([dim_x, part_y, dim_x, part_y+part_h], fill='black', width=2)
    draw.line([dim_x-10, part_y, dim_x+10, part_y], fill='black', width=2)
    draw.line([dim_x-10, part_y+part_h, dim_x+10, part_y+part_h], fill='black', width=2)
    # Arrow heads
    draw.polygon([dim_x, part_y+10, dim_x-5, part_y, dim_x+5, part_y], fill='black')
    draw.polygon([dim_x, part_y+part_h-10, dim_x-5, part_y+part_h, dim_x+5, part_y+part_h], fill='black')
    draw.text((dim_x - 50, part_y + part_h/2 - 20), "250mm", fill='black', font=font_medium)
    
    # Internal features with labels
    # Mounting holes
    holes = [
        (300, 370, "HOLE A"),
        (700, 370, "HOLE B"),
        (300, 480, "HOLE C"),
        (700, 480, "HOLE D")
    ]
    for x, y, label in holes:
        draw.ellipse([x-20, y-20, x+20, y+20], outline='black', width=2)
        # Center mark
        draw.line([x-25, y, x+25, y], fill='black', width=1)
        draw.line([x, y-25, x, y+25], fill='black', width=1)
        # Label with leader line
        draw.line([x+25, y-25, x+60, y-40], fill='black', width=1)
        draw.text((x+65, y-50), label, fill='black', font=font_small)
        draw.text((x+65, y-30), "Ø20mm", fill='black', font=font_tiny)
    
    # Notes section
    notes_y = 620
    draw.line([50, notes_y, 950, notes_y], fill='black', width=2)
    draw.text((60, notes_y + 10), "NOTES:", fill='black', font=font_medium)
    draw.text((60, notes_y + 50), "1. ALL DIMENSIONS IN MILLIMETERS", fill='black', font=font_small)
    draw.text((60, notes_y + 75), "2. MATERIAL: ALUMINUM 6061-T6", fill='black', font=font_small)
    draw.text((60, notes_y + 100), "3. TOLERANCES: ±0.1mm UNLESS NOTED", fill='black', font=font_small)
    
    # Part number callout
    draw.ellipse([480, 380, 520, 420], outline='black', width=2)
    draw.text((488, 390), "1", fill='black', font=font_medium)
    draw.line([520, 400, 580, 350], fill='black', width=1)
    draw.text((585, 335), "PART NO: A-12345", fill='black', font=font_small)
    
    img.save('test_images/test6_text_labels.png')
    print("Created test6_text_labels.png")


def create_test_image_7_geodesic_dome():
    """Geodesic dome blueprint - complex structure with many triangular faces"""
    img = Image.new('RGB', (1200, 1000), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use fonts for labels
    try:
        from PIL import ImageFont
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except:
        font_small = None
        font_tiny = None
    
    # Title block
    draw.rectangle([50, 50, 1150, 120], outline='black', width=3)
    draw.line([50, 85, 1150, 85], fill='black', width=2)
    draw.text((70, 60), "GEODESIC DOME - 3V ICOSAHEDRON", fill='black', font=font_small)
    draw.text((70, 95), "SCALE: 1:50  |  RADIUS: 5.0m  |  STRUT TYPES: A, B, C", fill='black', font=font_tiny)
    
    # Generate 3V geodesic dome vertices
    # Using simplified icosahedron-based geodesic dome
    cx, cy = 600, 550  # Center of dome
    radius = 380
    
    # Define icosahedron vertices (top hemisphere + base)
    phi = (1 + math.sqrt(5)) / 2  # Golden ratio
    
    # Create vertices for a 3-frequency geodesic dome
    vertices_3d = []
    
    # Method: Create vertices on a sphere using icosahedron subdivision
    # Start with icosahedron vertices
    ico_verts = [
        (0, 1, phi), (0, -1, phi), (0, 1, -phi), (0, -1, -phi),
        (1, phi, 0), (-1, phi, 0), (1, -phi, 0), (-1, -phi, 0),
        (phi, 0, 1), (-phi, 0, 1), (phi, 0, -1), (-phi, 0, -1)
    ]
    
    # Normalize to unit sphere
    ico_verts = [(x/math.sqrt(x*x+y*y+z*z), y/math.sqrt(x*x+y*y+z*z), z/math.sqrt(x*x+y*y+z*z)) 
                 for x, y, z in ico_verts]
    
    # Create icosahedron faces (only upper hemisphere)
    faces = [
        (0, 4, 1), (0, 1, 9), (1, 8, 9), (1, 4, 8), (4, 0, 5),
        (4, 5, 10), (4, 10, 8), (8, 10, 6), (8, 6, 9), (9, 6, 11),
        (9, 11, 5), (9, 5, 0), (5, 11, 2), (5, 2, 10), (10, 2, 3),
        (10, 3, 6), (6, 3, 7), (6, 7, 11), (11, 7, 2), (2, 7, 3)
    ]
    
    # Subdivide each face into smaller triangles (frequency 3)
    def midpoint(p1, p2):
        """Calculate midpoint on sphere surface"""
        mx, my, mz = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2
        length = math.sqrt(mx*mx + my*my + mz*mz)
        return (mx/length, my/length, mz/length)
    
    # Collect all unique vertices
    all_verts = set()
    subdivided_faces = []
    
    for face in faces:
        v1, v2, v3 = ico_verts[face[0]], ico_verts[face[1]], ico_verts[face[2]]
        
        # Skip if mostly below horizon (negative z)
        if v1[2] < -0.2 and v2[2] < -0.2 and v3[2] < -0.2:
            continue
        
        # Simple subdivision - create 3 vertices on edges
        m12 = midpoint(v1, v2)
        m23 = midpoint(v2, v3)
        m31 = midpoint(v3, v1)
        
        # Create 4 sub-triangles
        sub_faces = [
            (v1, m12, m31),
            (m12, v2, m23),
            (m31, m23, v3),
            (m12, m23, m31)
        ]
        
        for sf in sub_faces:
            # Further subdivide once more for frequency 3
            sm1, sm2, sm3 = sf[0], sf[1], sf[2]
            sm12 = midpoint(sm1, sm2)
            sm23 = midpoint(sm2, sm3)
            sm31 = midpoint(sm3, sm1)
            
            final_faces = [
                (sm1, sm12, sm31),
                (sm12, sm2, sm23),
                (sm31, sm23, sm3),
                (sm12, sm23, sm31)
            ]
            
            for ff in final_faces:
                subdivided_faces.append(ff)
                all_verts.add(ff[0])
                all_verts.add(ff[1])
                all_verts.add(ff[2])
    
    # Project 3D vertices to 2D (orthographic projection)
    def project_vertex(v):
        x, y, z = v
        # Rotate for better view
        angle = math.pi / 6
        rx = x * math.cos(angle) - y * math.sin(angle)
        ry = x * math.sin(angle) + y * math.cos(angle)
        
        # Project to 2D
        scale = radius
        px = cx + rx * scale
        py = cy - z * scale - ry * scale * 0.3
        return (px, py)
    
    # Draw all edges (struts)
    drawn_edges = set()
    strut_counts = {'A': 0, 'B': 0, 'C': 0}
    
    for face in subdivided_faces:
        v1, v2, v3 = face
        edges = [(v1, v2), (v2, v3), (v3, v1)]
        
        for edge in edges:
            # Normalize edge (sort to avoid duplicates)
            normalized_edge = tuple(sorted([edge[0], edge[1]]))
            
            if normalized_edge not in drawn_edges:
                drawn_edges.add(normalized_edge)
                p1 = project_vertex(edge[0])
                p2 = project_vertex(edge[1])
                
                # Calculate edge length type (3 different lengths in geodesic dome)
                length = math.sqrt(sum((a-b)**2 for a, b in zip(edge[0], edge[1])))
                if length < 0.35:
                    color = 'black'
                    width = 2
                    strut_type = 'A'
                elif length < 0.38:
                    color = 'black'
                    width = 2
                    strut_type = 'B'
                else:
                    color = 'black'
                    width = 2
                    strut_type = 'C'
                
                strut_counts[strut_type] += 1
                draw.line([p1[0], p1[1], p2[0], p2[1]], fill=color, width=width)
    
    # Draw base circle
    base_y = cy + radius * 0.4
    draw.ellipse([cx-radius*0.95, base_y-30, cx+radius*0.95, base_y+30], outline='black', width=3)
    
    # Draw vertices (hubs)
    for v in list(all_verts)[:20]:  # Draw some key vertices
        if v[2] > -0.1:  # Only visible ones
            p = project_vertex(v)
            draw.ellipse([p[0]-3, p[1]-3, p[0]+3, p[1]+3], fill='black')
    
    # Dimension line for radius
    dim_y = cy - radius - 50
    draw.line([cx, dim_y, cx + radius*0.8, dim_y], fill='black', width=1)
    draw.line([cx, dim_y-10, cx, dim_y+10], fill='black', width=1)
    draw.line([cx + radius*0.8, dim_y-10, cx + radius*0.8, dim_y+10], fill='black', width=1)
    # Arrows
    draw.polygon([cx+10, dim_y, cx, dim_y-5, cx, dim_y+5], fill='black')
    draw.polygon([cx + radius*0.8-10, dim_y, cx + radius*0.8, dim_y-5, cx + radius*0.8, dim_y+5], fill='black')
    draw.text((cx + radius*0.3, dim_y - 25), "R = 5.0m", fill='black', font=font_small)
    
    # Legend for strut types
    legend_x, legend_y = 900, 200
    draw.rectangle([legend_x-10, legend_y-10, legend_x+220, legend_y+110], outline='black', width=2)
    draw.text((legend_x, legend_y), "STRUT SCHEDULE:", fill='black', font=font_small)
    draw.line([legend_x, legend_y+25, legend_x+50, legend_y+25], fill='black', width=2)
    draw.text((legend_x+60, legend_y+20), f"TYPE A: {strut_counts['A']} pcs (1.23m)", fill='black', font=font_tiny)
    draw.line([legend_x, legend_y+50, legend_x+50, legend_y+50], fill='black', width=2)
    draw.text((legend_x+60, legend_y+45), f"TYPE B: {strut_counts['B']} pcs (1.28m)", fill='black', font=font_tiny)
    draw.line([legend_x, legend_y+75, legend_x+50, legend_y+75], fill='black', width=2)
    draw.text((legend_x+60, legend_y+70), f"TYPE C: {strut_counts['C']} pcs (1.31m)", fill='black', font=font_tiny)
    
    # Notes
    notes_y = 850
    draw.line([50, notes_y, 1150, notes_y], fill='black', width=2)
    draw.text((60, notes_y+10), "NOTES:", fill='black', font=font_small)
    draw.text((60, notes_y+35), "1. ALL STRUTS ARE ALUMINUM TUBE Ø60mm x 3mm WALL", fill='black', font=font_tiny)
    draw.text((60, notes_y+55), "2. HUB CONNECTORS: 6-WAY GALVANIZED STEEL", fill='black', font=font_tiny)
    draw.text((60, notes_y+75), "3. COVERING: UV-RESISTANT POLYCARBONATE PANELS", fill='black', font=font_tiny)
    draw.text((60, notes_y+95), "4. FOUNDATION: CONCRETE PIERS AT BASE VERTICES", fill='black', font=font_tiny)
    
    img.save('test_images/test7_geodesic_dome.png')
    print("Created test7_geodesic_dome.png")


def create_test_image_8_interlocking_gears():
    """Blueprint of interlocking gears of various sizes"""
    img = Image.new('RGB', (1400, 1000), color='white')
    draw = ImageDraw.Draw(img)
    
    def draw_gear(cx, cy, outer_radius, num_teeth, tooth_depth, shaft_radius):
        """Draw a gear with given parameters"""
        # Calculate inner radius (base of teeth)
        inner_radius = outer_radius - tooth_depth
        
        # Draw outer circle (reference)
        draw.ellipse([cx-outer_radius, cy-outer_radius, 
                     cx+outer_radius, cy+outer_radius], 
                     outline='black', width=2)
        
        # Draw inner circle (root of teeth)
        draw.ellipse([cx-inner_radius, cy-inner_radius, 
                     cx+inner_radius, cy+inner_radius], 
                     outline='black', width=2)
        
        # Draw teeth
        for i in range(num_teeth):
            angle1 = (i * 2 * math.pi / num_teeth) - (math.pi / (2 * num_teeth))
            angle2 = (i * 2 * math.pi / num_teeth) + (math.pi / (2 * num_teeth))
            angle_mid = i * 2 * math.pi / num_teeth
            
            # Outer points of tooth
            x1_outer = cx + outer_radius * math.cos(angle1)
            y1_outer = cy + outer_radius * math.sin(angle1)
            x2_outer = cx + outer_radius * math.cos(angle2)
            y2_outer = cy + outer_radius * math.sin(angle2)
            
            # Inner points (root of tooth)
            x1_inner = cx + inner_radius * math.cos(angle1)
            y1_inner = cy + inner_radius * math.sin(angle1)
            x2_inner = cx + inner_radius * math.cos(angle2)
            y2_inner = cy + inner_radius * math.sin(angle2)
            
            # Draw tooth sides
            draw.line([x1_inner, y1_inner, x1_outer, y1_outer], fill='black', width=2)
            draw.line([x2_inner, y2_inner, x2_outer, y2_outer], fill='black', width=2)
            
            # Draw tooth top (arc approximation with short line)
            draw.line([x1_outer, y1_outer, x2_outer, y2_outer], fill='black', width=2)
        
        # Draw shaft/center hole
        draw.ellipse([cx-shaft_radius, cy-shaft_radius, 
                     cx+shaft_radius, cy+shaft_radius], 
                     outline='black', width=3)
        
        # Draw center cross for alignment
        cross_size = shaft_radius * 0.6
        draw.line([cx-cross_size, cy, cx+cross_size, cy], fill='black', width=2)
        draw.line([cx, cy-cross_size, cx, cy+cross_size], fill='black', width=2)
        
        return inner_radius  # Return for pitch circle reference
    
    # Title block
    draw.rectangle([50, 50, 1350, 120], outline='black', width=3)
    draw.line([50, 85, 1350, 85], fill='black', width=2)
    try:
        from PIL import ImageFont
        font_title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
        font_normal = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
        font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
    except:
        font_title = font_normal = font_small = None
    
    draw.text((60, 55), "MECHANICAL DRAWING: GEAR TRAIN ASSEMBLY", fill='black', font=font_title)
    draw.text((60, 95), "SCALE: 1:5  |  MATERIAL: STEEL  |  DWG NO: GT-2025-001", fill='black', font=font_small)
    
    # Define gear specifications
    # Gear 1: Large gear (left side)
    gear1_x, gear1_y = 350, 400
    gear1_outer = 180
    gear1_teeth = 48
    gear1_tooth_depth = 20
    gear1_shaft = 25
    
    # Gear 2: Medium gear (top right)
    gear2_x, gear2_y = 700, 280
    gear2_outer = 120
    gear2_teeth = 32
    gear2_tooth_depth = 15
    gear2_shaft = 20
    
    # Gear 3: Medium gear (bottom right, meshes with gear 1)
    gear3_x = gear1_x + (gear1_outer - gear1_tooth_depth) + (gear2_outer - gear2_tooth_depth)
    gear3_y = gear1_y
    gear3_outer = 120
    gear3_teeth = 32
    gear3_tooth_depth = 15
    gear3_shaft = 20
    
    # Gear 4: Small gear (far right, meshes with gear 2 and gear 3)
    gear4_outer = 80
    gear4_teeth = 24
    gear4_tooth_depth = 12
    gear4_shaft = 15
    
    # Position gear 4 to mesh with gear 3
    distance_3_4 = (gear3_outer - gear3_tooth_depth) + (gear4_outer - gear4_tooth_depth)
    gear4_x = gear3_x + distance_3_4
    gear4_y = gear3_y
    
    # Gear 5: Small gear (meshes with gear 2 from bottom)
    distance_2_5 = (gear2_outer - gear2_tooth_depth) + (gear4_outer - gear4_tooth_depth)
    gear5_x = gear2_x
    gear5_y = gear2_y + distance_2_5
    gear5_outer = gear4_outer
    gear5_teeth = gear4_teeth
    gear5_tooth_depth = gear4_tooth_depth
    gear5_shaft = gear4_shaft
    
    # Draw all gears
    draw_gear(gear1_x, gear1_y, gear1_outer, gear1_teeth, gear1_tooth_depth, gear1_shaft)
    draw_gear(gear2_x, gear2_y, gear2_outer, gear2_teeth, gear2_tooth_depth, gear2_shaft)
    draw_gear(gear3_x, gear3_y, gear3_outer, gear3_teeth, gear3_tooth_depth, gear3_shaft)
    draw_gear(gear4_x, gear4_y, gear4_outer, gear4_teeth, gear4_tooth_depth, gear4_shaft)
    draw_gear(gear5_x, gear5_y, gear5_outer, gear5_teeth, gear5_tooth_depth, gear5_shaft)
    
    # Dimension lines and annotations
    # Gear 1 annotation
    draw.text((gear1_x-50, gear1_y+200), "GEAR A", fill='black', font=font_normal)
    draw.text((gear1_x-50, gear1_y+220), f"T={gear1_teeth}", fill='black', font=font_small)
    draw.text((gear1_x-50, gear1_y+235), f"Ø{gear1_outer*2}mm", fill='black', font=font_small)
    
    # Dimension line for gear 1 diameter
    dim_y = gear1_y + 250
    draw.line([gear1_x-gear1_outer, dim_y, gear1_x+gear1_outer, dim_y], fill='black', width=1)
    draw.line([gear1_x-gear1_outer, dim_y-10, gear1_x-gear1_outer, dim_y+10], fill='black', width=1)
    draw.line([gear1_x+gear1_outer, dim_y-10, gear1_x+gear1_outer, dim_y+10], fill='black', width=1)
    
    # Gear 2 annotation
    draw.text((gear2_x-30, gear2_y-140), "GEAR B", fill='black', font=font_normal)
    draw.text((gear2_x-30, gear2_y-120), f"T={gear2_teeth}", fill='black', font=font_small)
    
    # Gear 3 annotation  
    draw.text((gear3_x-30, gear3_y+160), "GEAR C", fill='black', font=font_normal)
    draw.text((gear3_x-30, gear3_y+180), f"T={gear3_teeth}", fill='black', font=font_small)
    
    # Gear 4 annotation
    draw.text((gear4_x-25, gear4_y+110), "GEAR D", fill='black', font=font_normal)
    draw.text((gear4_x-25, gear4_y+130), f"T={gear4_teeth}", fill='black', font=font_small)
    
    # Gear 5 annotation
    draw.text((gear5_x+90, gear5_y-10), "GEAR E", fill='black', font=font_normal)
    draw.text((gear5_x+90, gear5_y+10), f"T={gear5_teeth}", fill='black', font=font_small)
    
    # Center distance annotations (with leader lines)
    # Distance between gear 1 and gear 3
    mid_x = (gear1_x + gear3_x) / 2
    draw.line([gear1_x, gear1_y-30, gear3_x, gear3_y-30], fill='black', width=1)
    draw.line([gear1_x, gear1_y-35, gear1_x, gear1_y-25], fill='black', width=1)
    draw.line([gear3_x, gear3_y-35, gear3_x, gear3_y-25], fill='black', width=1)
    draw.text((mid_x-30, gear1_y-50), f"C={int(gear3_x-gear1_x)}mm", fill='black', font=font_small)
    
    # Legend/specifications box
    legend_x = 950
    legend_y = 650
    draw.rectangle([legend_x-20, legend_y-20, legend_x+400, legend_y+280], outline='black', width=2)
    draw.text((legend_x, legend_y), "GEAR SPECIFICATIONS:", fill='black', font=font_normal)
    
    y_offset = legend_y + 30
    specs = [
        f"GEAR A: {gear1_teeth} teeth, PCD {(gear1_outer-gear1_tooth_depth)*2}mm",
        f"GEAR B: {gear2_teeth} teeth, PCD {(gear2_outer-gear2_tooth_depth)*2}mm",
        f"GEAR C: {gear3_teeth} teeth, PCD {(gear3_outer-gear3_tooth_depth)*2}mm",
        f"GEAR D: {gear4_teeth} teeth, PCD {(gear4_outer-gear4_tooth_depth)*2}mm",
        f"GEAR E: {gear5_teeth} teeth, PCD {(gear5_outer-gear5_tooth_depth)*2}mm",
        "",
        f"MODULE: 2.5mm",
        f"PRESSURE ANGLE: 20°",
        f"MATERIAL: EN24 STEEL",
        f"HARDNESS: 58-62 HRC",
        f"SURFACE FINISH: Ra 1.6",
    ]
    
    for i, spec in enumerate(specs):
        draw.text((legend_x, y_offset + i*22), spec, fill='black', font=font_small)
    
    # Notes section
    notes_y = 180
    draw.line([50, notes_y, 900, notes_y], fill='black', width=2)
    draw.text((60, notes_y+10), "NOTES:", fill='black', font=font_normal)
    draw.text((60, notes_y+35), "1. ALL GEARS TO BE CUT WITH GEAR HOBBING MACHINE", fill='black', font=font_small)
    draw.text((60, notes_y+55), "2. HEAT TREAT AFTER CUTTING: CARBURIZE AND HARDEN", fill='black', font=font_small)
    draw.text((60, notes_y+75), "3. SHAFT TOLERANCES: H7/k6 FIT", fill='black', font=font_small)
    
    img.save('test_images/test8_interlocking_gears.png')
    print("Created test8_interlocking_gears.png")


def main():
    import os
    os.makedirs('test_images', exist_ok=True)
    
    print("Generating test images...")
    create_test_image_1_simple_box()
    create_test_image_2_floor_plan()
    create_test_image_3_geometric()
    create_test_image_4_mechanical()
    create_test_image_5_circuit()
    create_test_image_6_text_labels()
    create_test_image_7_geodesic_dome()
    create_test_image_8_interlocking_gears()
    print("\nAll test images created in 'test_images/' directory")


if __name__ == '__main__':
    main()
