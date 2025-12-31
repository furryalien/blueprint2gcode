# Solid Area Filling - Quick Start Guide

## Problem Statement
Previously, solid black areas in images were only rendered as outlines, which didn't visually represent the filled nature of these regions.

## Solution
The blueprint2gcode converter now detects solid black areas and fills them with cross-hatching patterns.

## Quick Start

### 1. Generate Test Images (Optional)
```bash
python generate_solid_test_images.py
```
Creates 8 test images in `test_images_solid/` directory.

### 2. Basic Usage

#### Without Solid Filling (Old Behavior)
```bash
python blueprint2gcode.py input.png output.gcode
```
Result: Only outlines are drawn

#### With Solid Filling (New Feature)
```bash
python blueprint2gcode.py input.png output.gcode --fill-solid-areas
```
Result: Solid areas are filled with cross-hatching

### 3. Customize Hatching

#### Adjust Hatch Density
```bash
# Dense hatching (more lines)
python blueprint2gcode.py input.png output.gcode --fill-solid-areas --hatch-spacing 0.5

# Sparse hatching (fewer lines)
python blueprint2gcode.py input.png output.gcode --fill-solid-areas --hatch-spacing 3.0
```

#### Adjust Hatch Angle
```bash
# Horizontal lines
python blueprint2gcode.py input.png output.gcode --fill-solid-areas --hatch-angle 0

# Vertical lines
python blueprint2gcode.py input.png output.gcode --fill-solid-areas --hatch-angle 90

# Diagonal lines (default)
python blueprint2gcode.py input.png output.gcode --fill-solid-areas --hatch-angle 45
```

#### Filter Small Areas
```bash
# Only fill areas larger than 500 pixels
python blueprint2gcode.py input.png output.gcode --fill-solid-areas --min-solid-area 500
```

### 4. Run Comprehensive Tests
```bash
# Run full test suite with 18+ configurations
python test_harness_solid.py
```

### 5. Visualize Results
```bash
# Create comparison visualization
python visualize_solid_comparison.py
```

## Parameters Reference

| Parameter | Default | Description | Example Values |
|-----------|---------|-------------|----------------|
| `--fill-solid-areas` | disabled | Enable solid area filling | (flag, no value) |
| `--hatch-spacing` | 1.0 | Spacing between hatch lines (pixels) | 0.5 (dense), 3.0 (sparse) |
| `--hatch-angle` | 45.0 | Angle of hatch lines (degrees) | 0 (horizontal), 90 (vertical) |
| `--min-solid-area` | 100.0 | Minimum area to fill (pixels) | 50 (fill small), 500 (fill large only) |

## When to Use Each Setting

### Hatch Spacing
- **0.5px** - Very dense fill, photographic quality, slow to plot
- **1.0px** - Standard fill, good balance (default)
- **2.0px** - Medium fill, faster plotting
- **3.0px** - Sparse fill, quick preview, artistic look

### Hatch Angle
- **0°** - Horizontal lines, good for floor plans
- **45°** - Diagonal lines, classic hatching (default)
- **90°** - Vertical lines, technical drawings
- **135°** - Opposite diagonal, can combine with 45° for cross-hatch

### Minimum Solid Area
- **50px** - Fill almost everything including small details
- **100px** - Standard, filters minor artifacts (default)
- **200px** - Medium, only fill moderate-sized areas
- **500px** - Large, only fill significant solid regions

## Common Use Cases

### Floor Plans with Solid Walls
```bash
python blueprint2gcode.py floor_plan.png output.gcode \
    --fill-solid-areas \
    --hatch-spacing 2.0 \
    --hatch-angle 45
```

### Mechanical Parts with Solid Sections
```bash
python blueprint2gcode.py mechanical.png output.gcode \
    --fill-solid-areas \
    --hatch-spacing 1.5 \
    --hatch-angle 45
```

### Logos or Designs with Solid Elements
```bash
python blueprint2gcode.py logo.png output.gcode \
    --fill-solid-areas \
    --hatch-spacing 1.0 \
    --min-solid-area 200
```

### Circuit Boards with Solid Pads
```bash
python blueprint2gcode.py circuit.png output.gcode \
    --fill-solid-areas \
    --hatch-spacing 1.0 \
    --min-solid-area 50
```

## Troubleshooting

### Problem: Small artifacts are being filled
**Solution**: Increase `--min-solid-area` to 200 or 500

### Problem: Hatching is too dense, taking too long
**Solution**: Increase `--hatch-spacing` to 2.0 or 3.0

### Problem: Hatching is too sparse, not visible enough
**Solution**: Decrease `--hatch-spacing` to 0.5 or 0.75

### Problem: Some solid areas not being filled
**Solution**: Decrease `--min-solid-area` to 50 or lower

### Problem: Outlines being drawn twice
**Solution**: This shouldn't happen - solid areas are removed from line detection. If it does occur, report as a bug.

## Expected Results

### Test 1: Simple Shapes
- **Without fill**: ~5 line segments (just outlines)
- **With fill**: ~980 line segments (outlines + hatching)
- **Plot time**: Increases from ~1.5 min to ~34 min

### Visual Comparison
The visualization tool creates side-by-side comparisons showing the dramatic difference between outline-only and filled rendering.

## Tips
- Start with default settings, then adjust based on results
- Preview with `--hatch-spacing 3.0` for quick tests
- Use `--min-solid-area 500` to only fill large regions first
- For cross-hatching effect, run twice with angles 45° and 135°
- Higher resolution input images allow for finer hatch spacing
