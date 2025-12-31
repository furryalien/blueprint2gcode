# Mechanical Part Fill Fix - Holes vs Solid Areas

## Problem Report
User reported that the fill was still incorrect in the mechanical part image. The screenshot showed:
- **Expected**: Black rectangle filled with hatching, white circular holes left empty
- **Actual**: White circular holes were being filled instead of (or in addition to) the black rectangle

## Root Cause Analysis

### Contour Structure
```
Contour 0: Parent (241,144px, solidity=0.668)
  └─ Contour 1: Child - hole (3,971px, solidity=0.992)  
  └─ Contour 2: Child - hole (4,073px, solidity=0.992)
  └─ Contour 3: Child - hole (8,133px, solidity=0.992)
  └─ Contour 4: Child - hole (8,133px, solidity=0.992)
```

### Issues Found

1. **Parent Not Detected**: The main rectangle (Contour 0) had solidity of 0.668 (< 0.7 threshold) because the holes reduce the solidity ratio. The initial logic only checked `if solidity > 0.7`, so it never evaluated the parent.

2. **Children Being Filled**: Child contours (the holes) had very high solidity (0.992) and low compactness (14-18), matching the criteria intended for floor plan walls. They were being incorrectly filled.

3. **Ambiguous Logic**: The code couldn't distinguish between:
   - **Floor plan walls**: Child rectangles that ARE solid (should be filled)
   - **Mechanical holes**: Child circles that are HOLES in a solid parent (should NOT be filled)

## Solution Implemented

### Three-Part Fix

**1. Check Parents First** (before the solidity threshold):
```python
if has_children and not is_child:
    # Parent with holes - accept if solidity > 0.5 and reasonable compactness
    if solidity > 0.5 and compactness < 200:
        is_solid = True
        parent_indices.add(i)  # Track this parent
```

**2. Track Parent Indices**:
Added `parent_indices` set to remember which contours are solid parents that will be filled.

**3. Exclude Children of Solid Parents**:
```python
elif is_child:
    # Check if this child's parent is already marked as solid
    parent_idx = hierarchy[i][3]
    if parent_idx not in parent_indices:
        # Parent is not solid, so this might be a standalone filled child
        # (like floor plan walls)
        if solidity > 0.95 and compactness < 50:
            is_solid = True
    # else: parent is solid, so don't fill the holes
```

## Test Results

### Before Fix
```
Found 5 solid areas  ← WRONG: includes 4 holes + maybe parent
Generated 377 hatch lines
Lines: 381
```
Visualization showed holes being filled.

### After Fix
```
Found 1 solid area   ← CORRECT: only the parent rectangle
Generated 3271 hatch lines
Lines: 1676
Drawing distance: 254,225mm
```

Visualization confirms:
- ✅ Black rectangle is completely hatched
- ✅ White circular holes are left empty
- ✅ Alignment marks (crosshairs) are preserved as outlines

## Floor Plan Compatibility

The floor plan still works correctly with 3 detected areas:
- Contour 46: Parent (outer perimeter, 480k area) 
- Contours 47-48: Children (room interiors) - correctly NOT filled since parent is filled
- Contours 12, 17: Small standalone features

## Key Insight

The hierarchy distinguishes:
- **Parent → Children**: Solid area with holes inside (mechanical part)
  - Fill parent, exclude children
- **Orphan children**: Filled rectangles with no solid parent (floor plan walls)  
  - Fill children if parent not in parent_indices set

This allows the same logic to handle both cases correctly!

## Files Modified

1. **blueprint2gcode.py** - Updated `detect_solid_areas()` method:
   - Added `parent_indices` tracking (line 72)
   - Reordered logic to check parents before solidity threshold (lines 110-114)
   - Added parent tracking when marking parent as solid (line 114)
   - Modified child detection to exclude children of solid parents (lines 122-129)

## Validation

✅ Mechanical part: 1 solid area (main rectangle only)
✅ Floor plan: 3 solid areas (outer walls + small features)
✅ Simple shapes: 5 solid areas (5 separate shapes)

All visualizations show correct hatching within boundaries!
