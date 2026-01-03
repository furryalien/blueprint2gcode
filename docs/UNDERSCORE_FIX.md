# Underscore Fix - Complete

## Problem
Underscores and other thin horizontal shapes (like minus signs) were not being properly filled when using the `--fill-solid-areas` option. The issue was that diagonal hatch lines (at 45°) with standard spacing (2.16px) would completely miss thin horizontal shapes that are only 3-4 pixels tall.

## Root Cause
When hatching at 45° with 2.16px spacing on a 4px tall horizontal rectangle:
- Many hatch lines would pass above or below the shape entirely
- Only a few lines might clip the edges, resulting in poor or no fill

## Solution
Added special case detection for thin horizontal and vertical shapes in `generate_hatch_lines()`:

### Detection Criteria
- **Thin horizontal**: `height < 8 pixels` AND `width/height > 4`
- **Thin vertical**: `width < 8 pixels` AND `height/width > 4`

### Fill Strategy
For thin horizontal shapes (like underscores):
- Generate horizontal lines spaced vertically at ~1px intervals
- Use dense spacing (1px or height/2, whichever is smaller) to ensure complete coverage
- Generate at least 2 lines, typically 4-5 lines for 4px tall shapes

For thin vertical shapes:
- Generate vertical lines spaced horizontally using the same logic

## Implementation Details

Location: `blueprint2gcode.py`, `generate_hatch_lines()` function (lines ~220-300)

```python
# Detect thin horizontal shapes
is_thin_horizontal = (h < 8) and (w / h > 4)

if is_thin_horizontal:
    # Generate horizontal lines with dense vertical spacing
    vert_spacing = min(1.0, h / 2.0) if h > 2 else 1.0
    num_lines = max(int(h / vert_spacing) + 1, 2)
    
    for i in range(num_lines):
        y_line = ... # Calculate Y coordinate
        # Find exact boundaries using mask
        # Generate horizontal line from x_min to x_max
```

## Test Results

Test image: 5 numbers (1-5) with underscores of increasing length

**Before fix:**
- Underscores detected but 0 lines generated (diagonal hatching missed them)

**After fix:**
- 5 underscores × 4 horizontal lines each = 20 underscore lines
- All underscores properly filled
- Numbers continue to use crosshatch pattern

### Output Statistics
- Total drawing lines: 310
- Underscore lines (horizontal, >20mm): 20
- Drawing distance: 1951.79 mm
- Estimated time: 2.1 minutes

## Files Modified
- `blueprint2gcode.py`: Added thin shape detection and horizontal/vertical fill logic

## Testing
Run with: 
```bash
python3 blueprint2gcode.py test_underscores.png output.gcode --fill-solid-areas --hatch-spacing 1.5
```

## Benefits
- Underscores now properly filled
- Works for other thin shapes (minus signs, horizontal rules, etc.)
- Also handles thin vertical shapes (vertical bars, pipes, etc.)
- Maintains proper coverage without gaps

## Notes
- The fix uses horizontal/vertical lines regardless of the `--hatch-angle` setting
- In `--crosshatch` mode, the same horizontal lines are used for both passes (no perpendicular lines needed for 1D shapes)
- Detection threshold (h < 8, aspect ratio > 4) can be adjusted if needed
