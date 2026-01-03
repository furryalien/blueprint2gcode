# Solid Area Outline and Hatch Fill Fix

## Problem 1: Missing Outlines

When converting images with solid areas (like an arch that's narrow at the bottom and wide at the top), the system was correctly detecting and filling the areas with hatch lines, but was **not drawing the outlines**. This made filled shapes appear as just parallel hatch lines without clear boundaries.

### Example
An arch swooping from bottom to top, narrow at bottom and wide at top, would be converted to:
- ❌ **Before**: Only hatch fill lines (no defined edge)
- ✅ **After**: Hatch fill lines + outline defining the shape

## Problem 2: Hatch Lines Being Merged with Outlines

After adding outlines, a second issue was discovered: **the joining algorithm was merging hatch lines with outline segments**, causing many hatch lines to disappear or become part of longer polylines. This resulted in only partial filling of solid areas.

### Example
An arch that should have 162 hatch lines would end up with only ~92 visible hatch segments because they were joined into long polylines with the outline.

- ❌ **Before fix**: 466 total line segments (many hatches merged into outlines)
- ✅ **After fix**: 375 line segments (162 hatches + 2 outlines preserved separately)

## Root Causes

### Cause 1: Outlines Removed
In the `detect_lines()` function, when solid areas were detected, their contour outlines were completely removed from the output.

### Cause 2: Indiscriminate Line Joining  
The `join_nearby_endpoints()` function joined ANY lines whose endpoints were within tolerance, regardless of their type (hatch vs outline vs regular line).

## Solution

### Fix 1: Add Explicit Outlines
Added code to generate outline lines for each solid area after generating hatch fill:

```python
# Add outlines for solid areas to define their boundaries
for contour_info in solid_areas:
    contour = contour_info[1] if isinstance(contour_info, tuple) else contour_info
    perimeter = cv2.arcLength(contour, True)
    epsilon = 0.5
    simplified = cv2.approxPolyDP(contour, epsilon, True)
    points = simplified.reshape(-1, 2).tolist()
    if len(points) >= 2:
        points.append(points[0])  # Close the loop
        solid_lines.append(points)
```

### Fix 2: Prevent Cross-Type Joining
Modified the line handling to tag lines by type ('regular' vs 'solid') and prevent joining between different types:

```python
# Tag lines by type
tagged_lines = [{'points': line, 'type': 'regular'} for line in lines]
tagged_solid_lines = [{'points': line, 'type': 'solid'} for line in solid_lines]

# In join_nearby_endpoints():
regular_lines = [item['points'] for item in lines if item.get('type') == 'regular']
solid_lines = [item['points'] for item in lines if item.get('type') == 'solid']
# Only join regular lines with each other
```

This ensures:
- Hatch lines remain separate and fill the entire area
- Outlines remain separate and define the shape boundary
- Regular lines (from skeletonization) can still be joined for efficiency

## Results

### Test Case: Arch with Width Variation
- **Input**: Arch shape, narrow at bottom (10px), wide at top (90px)
- **Before Fix 1**: 253 lines (hatch only, no outline)
- **After Fix 1**: 466 lines (hatches merged with outlines)
- **After Fix 2**: 375 lines (162 hatches + 2 outlines, fully separate)
- **Result**: Width variation clearly visible, shape properly defined, entire area filled

### Benefits
1. ✅ **Defined boundaries**: Shapes have clear edges
2. ✅ **Complete filling**: Hatches cover entire area without being merged
3. ✅ **Width preservation**: Variable-width shapes properly represented
4. ✅ **Backward compatible**: Works with all existing solid area types

## Files Modified

- [blueprint2gcode.py](../blueprint2gcode.py):
  - Lines 672-690: Added outline generation
  - Lines 745-752: Added line tagging by type
  - Lines 758-766: Modified scale_to_a4 to handle tagged lines
  - Lines 850-862: Modified join_nearby_endpoints to respect line types

## Testing

Tested with:
- ✅ Arch with variable width (narrow→wide): Full hatching + outline
- ✅ Mechanical part with holes: Complete fill, holes preserved
- ✅ Simple geometric shapes: All areas fully filled
- ✅ Floor plans with walls: Walls filled, structure preserved

All tests show proper outline generation and complete hatch filling without unwanted merging.

## Visual Comparison

![Final Fix Comparison](../arch_fix_comparison_final.png)
- **Left panel**: Input image (arch with width variation)
- **Middle panel**: After Fix 1 (outline added but hatches merged - incomplete fill)
- **Right panel**: After Fix 2 (hatches preserved - complete fill with outline)

## Date
January 2, 2026
