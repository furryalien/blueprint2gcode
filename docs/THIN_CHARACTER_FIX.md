# Thin Character Detection Fix

## Problem
The number "1" (first character) was not being filled because its area (76 pixels) was below the default minimum solid area threshold (100 pixels).

## Root Cause
Very thin characters like "1", "i", "l" have small pixel areas even though they are clearly distinct shapes that should be filled. The default `--min-solid-area 100` filter was rejecting these thin characters.

## Solution
Added special exception for thin but tall/long shapes that bypasses the minimum area threshold.

### Detection Criteria
A shape is considered "thin but significant" if:
- **Thin and tall**: width < 20 pixels AND height > 15 pixels, OR
- **Thin and long**: height < 20 pixels AND width > 15 pixels

These shapes are detected even if their area is below `--min-solid-area`.

## Implementation

Location: `blueprint2gcode.py`, `detect_solid_areas()` function (lines ~95-105)

```python
# Exception: Very thin but tall/long shapes (like "1", "i", "l", "-")
# should be considered even if their area is small
is_thin_tall = (w < 20 and h > 15) or (h < 20 and w > 15)

if effective_area < self.min_solid_area and not is_thin_tall:
    continue
```

## Test Results

**Before fix:**
- First "1": area=76, **rejected** (< 100 threshold)
- Total solid areas detected: 9 (missing one "1")
- Lines in first "1" region: 0

**After fix:**
- First "1": area=76, **accepted** (thin and tall exception)
- Total solid areas detected: 10 (all numbers + underscores)
- Lines in first "1" region: 5
- Total lines: 359 (339 for numbers + 20 for underscores)

## Benefits
- Thin characters like "1", "i", "l" now properly detected
- Works with default `--min-solid-area 100` setting
- Also helps with thin horizontal elements like "-", "_" even if very small
- No impact on normal shapes (they still use area threshold)

## Related Fixes
This complements the earlier underscore fix (thin horizontal shape handling) to ensure all text characters are properly filled regardless of their dimensions.
