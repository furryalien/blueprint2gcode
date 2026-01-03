#!/usr/bin/env python3
"""Check what's in the raw G-code before path optimization"""

# Parse just the drawing commands
with open('test_output/underscores_debug.gcode') as f:
    lines = []
    current_pos = None
    pen_down = False
    
    for line in f:
        line = line.strip()
        if ';' in line:
            continue  # Skip comments
        
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

print(f"Total drawing lines: {len(lines)}")

# Look for horizontal lines in the underscore Y range
print("\nLooking for horizontal lines (±0.5mm in Y):")
horizontal_lines = []
for (x1, y1), (x2, y2) in lines:
    y_diff = abs(y2 - y1)
    x_diff = abs(x2 - x1)
    
    # Horizontal if Y difference is small
    if y_diff < 0.5 and x_diff > 5:
        horizontal_lines.append(((x1, y1), (x2, y2)))

print(f"Found {len(horizontal_lines)} horizontal lines")

# Group by Y coordinate
by_y = {}
for (x1, y1), (x2, y2) in horizontal_lines:
    y_avg = (y1 + y2) / 2
    y_bucket = round(y_avg, 1)
    if y_bucket not in by_y:
        by_y[y_bucket] = []
    by_y[y_bucket].append(((x1, y1), (x2, y2)))

print("\nHorizontal lines grouped by Y coordinate:")
for y in sorted(by_y.keys()):
    print(f"  Y ≈ {y:.1f}mm: {len(by_y[y])} lines")
    for (x1, y1), (x2, y2) in by_y[y][:3]:  # Show first 3
        print(f"      ({x1:.1f}, {y1:.1f}) → ({x2:.1f}, {y2:.1f})")

# Check underscore Y ranges
print("\nExpected underscore Y ranges (in mm):")
print("  _1: 38.1 - 40.9")
print("  _2: 72.8 - 75.6")
print("  _3: 107.5 - 110.3")
print("  _4: 142.1 - 144.9")
print("  _5: 176.8 - 179.6")
