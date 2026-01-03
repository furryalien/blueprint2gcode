# Crescent with Children Detection Fix

## Problem
The user provided an image (screen.jpg) with a long, curved brush stroke (crescent shape) that was not being filled with hatching. The shape had the following characteristics:
- Low solidity: 0.303 (due to curved/crescent shape)
- Moderate compactness: 263.1
- Good thickness: 8.65
- **Contains children**: Other smaller shapes overlapping inside the crescent

## Root Cause
The crescent detection special case (added previously) only worked for shapes **without children** (`not has_children`). The condition was:

```python
elif not has_children and not is_child and thickness >= min_thickness:
    if calc_area > 500 and thickness > 1.5 and compactness < 1500:
        is_solid = True
```

However, the longest crescent in screen.jpg had `has_children=True` because other shapes were overlapping inside it. This caused it to enter a different branch (parent with children handling) which required `solidity > 0.4`, but the crescent only had solidity=0.303.

## Solution
Added crescent detection logic **within** the parent-with-children branch, before the standard solidity check. This allows crescents/curved shapes to be detected even if they contain children.

### Code Changes
In `blueprint2gcode.py`, lines ~177-186:

```python
# For parent contours with children (holes), lower the solidity threshold
if has_children and not is_child:
    fill_ratio = (calc_area - children_area) / calc_area if calc_area > 0 else 0
    
    # Special case: Crescent/curved shapes with children inside
    # These have low solidity (0.25-0.40) but are clearly filled shapes, not outline strokes
    # e.g., thick curved brush strokes with other shapes overlapping inside
    if calc_area > 500 and thickness > 1.5 and compactness < 1500:
        is_solid = True
        parent_indices.add(i)  # Mark as parent so children are excluded
    # Only accept if [standard checks]...
    elif solidity > 0.4 and compactness < 200 and fill_ratio > 0.15 and thickness >= min_thickness:
        is_solid = True
        parent_indices.add(i)
```

Also updated the standalone crescent check (lines ~213-221) to remove the `not has_children` requirement (now just checks `not is_child`).

## Test Results

### screen.jpg (User's Image)
**Before Fix:**
- Solid areas detected: 1
- Hatch lines generated: 12
- Longest crescent: NOT filled (has_children=True, solidity=0.303)

**After Fix:**
- Solid areas detected: 2
- Hatch lines generated: 366 (827 total lines)
- Longest crescent: ✓ FILLED

### Regression Test (test6_crescent_spiral.png)
- Status: ✓ PASS
- Solid areas: 117 (unchanged)
- Hatch lines: 240 (unchanged)
- All 3 original crescent regions still working correctly

## Detection Criteria
Crescent/curved shapes are now detected as solid if they meet:
1. **Area**: > 500 pixels
2. **Thickness**: > 1.5 pixels (area/perimeter ratio)
3. **Compactness**: < 1500 (perimeter²/area)
4. **Parent status**: Can have children OR be standalone (not a child)
5. **Solidity**: Typically 0.10-0.40 (low due to curved shape)

This handles:
- Thin crescents without children (original fix)
- Thick curved brush strokes without children
- Crescent shapes with overlapping content inside (NEW)
- Curved shapes with variable width

## Files Modified
- `blueprint2gcode.py`: Lines 177-221 (crescent detection logic)

## Visualization
- Input: `screen.jpg`
- Output: `test_output/screen_test.gcode`
- Visualization: `screen_crescent_fixed.png`

## Date
January 3, 2026
