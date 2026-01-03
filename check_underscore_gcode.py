#!/usr/bin/env python3
"""Check if underscores are in the G-code output"""

def parse_gcode(filename):
    """Parse G-code and return drawing segments with coordinates"""
    lines = []
    with open(filename) as f:
        current_pos = None
        pen_down = False
        for line in f:
            line = line.strip()
            if 'Z3' in line or 'Z 3' in line:
                pen_down = False
            elif 'Z0' in line or 'Z 0' in line:
                pen_down = True
            elif line.startswith('G1 X') or line.startswith('G0 X'):
                parts = line.split()
                x = y = None
                for part in parts:
                    if part.startswith('X'):
                        x = float(part[1:])
                    elif part.startswith('Y'):
                        y = float(part[1:])
                if x and y:
                    new_pos = (x, y)
                    if current_pos and pen_down:
                        lines.append((current_pos, new_pos))
                    current_pos = new_pos
    return lines

gcode_lines = parse_gcode('test_output/underscores_test.gcode')

print(f"Total lines in G-code: {len(gcode_lines)}")

# Underscore regions in mm (converted from pixels with scale 0.6933)
underscore_regions = [
    (41.6, 38.1, 70.0, 40.9, '_1'),  # 60*0.6933, 55*0.6933, ..., '1'
    (41.6, 72.8, 84.0, 75.6, '_2'),
    (41.6, 107.5, 97.6, 110.3, '_3'),
    (41.6, 142.1, 111.6, 144.9, '_4'),
    (41.6, 176.8, 125.6, 179.6, '_5'),
]

print("\nChecking for lines in underscore regions:")
for x_min, y_min, x_max, y_max, label in underscore_regions:
    count = 0
    for (x1, y1), (x2, y2) in gcode_lines:
        # Check if line is within or crosses the underscore region
        if (x_min <= x1 <= x_max or x_min <= x2 <= x_max) and \
           (y_min <= y1 <= y_max or y_min <= y2 <= y_max):
            count += 1
    
    print(f"  {label}: {count} lines in region ({x_min:.1f}, {y_min:.1f}) - ({x_max:.1f}, {y_max:.1f})")
    if count == 0:
        print(f"      ⚠️  NO LINES FOUND - UNDERSCORE NOT FILLED!")
    else:
        print(f"      ✓ Lines found - underscore is filled")

# Also check number regions (approximately)
print("\nChecking for lines in number regions:")
number_regions = [
    (13.9, 38.1, 41.6, 60.0, '1'),
    (13.9, 72.8, 41.6, 94.7, '2'),
    (13.9, 107.5, 41.6, 129.4, '3'),
    (13.9, 142.1, 41.6, 164.0, '4'),
    (13.9, 176.8, 41.6, 198.7, '5'),
]

for x_min, y_min, x_max, y_max, label in number_regions:
    count = 0
    for (x1, y1), (x2, y2) in gcode_lines:
        if (x_min <= x1 <= x_max or x_min <= x2 <= x_max) and \
           (y_min <= y1 <= y_max or y_min <= y2 <= y_max):
            count += 1
    
    print(f"  {label}: {count} lines in region")
