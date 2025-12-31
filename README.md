# Blueprint to G-code Converter

Converts blueprint-style images (black lines on white background) to G-code for pen plotters and CNC machines with pen attachments.

## Features

- **Extreme Detail Detection**: Captures punctuation, small arrows, fine circuit traces, and delicate line work
- **Solid Area Filling**: Detects and fills solid black areas with configurable cross-hatching patterns
  - Automatically distinguishes between outlines and filled regions
  - Customizable hatch angle, spacing, and minimum area threshold
  - Preserves outline detection while adding fill patterns
- **Adaptive Simplification**: Intelligently preserves detail based on feature size:
  - Tiny features (<30px): 1000× less simplification for punctuation and arrows
  - Small features (<100px): 200× less simplification for fine text
  - Medium features (<300px): 50× less simplification for detailed work
  - Large features: 10× less simplification for efficiency
- **Accurate Line Detection**: Uses skeletonization and contour detection for smooth line extraction
- **Path Optimization**: Sophisticated nearest-neighbor algorithm minimizes pen travel
- **Line Joining**: Automatically connects nearby line endpoints to reduce pen lifts
- **Multiple Paper Sizes**: Supports A3, A4, A5, and A6 output formats
- **Flexible Orientation**: Auto-detect, force portrait, or force landscape with automatic 90° rotation
- **Highly Configurable**: Command-line options for all key parameters
- **Comprehensive Testing**: Includes test harness for validating all orientations and settings

## Project Structure

```
blueprint2gcode/
├── blueprint2gcode.py      # Main conversion script
├── README.md               # This file
├── docs/                   # Documentation and specifications
│   ├── requirements.txt    # Python dependencies
│   ├── spec.md            # Detailed specification
│   └── *.md               # Implementation notes and fix reports
├── tests/                  # All test scripts
│   ├── test_harness*.py   # Test harness scripts
│   ├── generate_*.py      # Test image generators
│   └── *.py               # Utility and analysis scripts
├── test_data/             # Test inputs and outputs
│   ├── test_images*/      # Test input images
│   ├── test_output*/      # Generated G-code files
│   └── test_results*      # Test result data
└── visualizations/        # Test visualizations
    └── test_visualizations*/  # Generated visualization images
```

## Installation

```bash
pip install -r docs/requirements.txt
```

## Usage

### Basic usage:

```bash
python blueprint2gcode.py input.jpg output.gcode
```

### With custom options:

```bash
# Specify paper size and orientation
python blueprint2gcode.py input.png output.gcode --paper-size A6 --orientation portrait

# Enable solid area filling with cross-hatching
python blueprint2gcode.py input.png output.gcode --fill-solid-areas

# Adjust hatching parameters
python blueprint2gcode.py input.png output.gcode \
    --fill-solid-areas \
    --hatch-spacing 1.5 \
    --hatch-angle 45 \
    --min-solid-area 100

# Adjust pen positions, speeds, and detail level
python blueprint2gcode.py input.png output.gcode \
    --z-up 5.0 \
    --z-down 0.0 \
    --feed-rate 1500 \
    --margin 5.0 \
    --join-tolerance 1.0 \
    --simplify-epsilon 0.000001
```

## Command-Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--z-up` | 3.0 | Z position for pen up (mm) |
| `--z-down` | 0.0 | Z position for pen down (mm) |
| `--feed-rate` | 1000 | Drawing speed (mm/min) |
| `--travel-rate` | 3000 | Travel speed when pen is up (mm/min) |
| `--paper-size` | A4 | Output paper size (A3, A4, A5, A6) |
| `--orientation` | auto | Output orientation (auto, portrait, landscape) |
| `--margin` | 1.0 | Margin around page (mm) |
| `--join-tolerance` | 0.02 | Max distance to join line endpoints (mm) |
| `--min-line-length` | 0.01 | Minimum line length to include (mm) |
| `--simplify-epsilon` | 0.000001 | Line simplification factor (lower = more detail) |
| `--fill-solid-areas` | disabled | Enable filling of solid black areas with hatching |
| `--hatch-spacing` | 1.0 | Spacing between hatch lines in pixels (before scaling) |
| `--hatch-angle` | 45.0 | Angle of hatch lines in degrees |
| `--min-solid-area` | 100.0 | Minimum area in pixels to consider as solid |

### Paper Sizes

| Size | Dimensions (mm) | Use Case |
|------|----------------|----------|
| A3 | 297 × 420 | Large detailed blueprints, posters |
| A4 | 210 × 297 | Standard documents (default) |
| A5 | 148 × 210 | Compact drawings, notebooks |
| A6 | 105 × 148 | Small sketches, postcards |

### Orientation Options

| Option | Behavior |
|--------|----------|
| `auto` | Automatically selects portrait or landscape based on image aspect ratio (default) |
| `portrait` | Forces portrait orientation, rotating image 90° if needed |
| `landscape` | Forces landscape orientation, rotating image 90° if needed |

## G-code Output

The generated G-code uses:
- **Absolute positioning** (G90)
- **Millimeter units** (G21)
- **Z-axis pen control**: Z0 for pen down, Z3 for pen up (configurable)
- **Feed rate**: 1000 mm/min for drawing (configurable)

## Input Requirements

- **Format**: JPG or PNG
- **Style**: Black lines on white background (blueprint style)
- **Quality**: Higher resolution images provide more accurate line detection

## Technical Details

### Solid Area Detection and Filling

When `--fill-solid-areas` is enabled, the converter:

1. **Detects solid regions** before skeletonization by finding contours with high solidity (>0.7)
2. **Generates cross-hatch patterns** at the specified angle and spacing
3. **Clips hatch lines** to stay within the boundary of each solid area
4. **Removes solid areas** from line detection to prevent double-drawing outlines
5. **Combines** hatch lines with detected outline lines for final output

Solid area detection uses:
- **Solidity threshold**: Area/Convex Hull Area > 0.7 (distinguishes filled vs outline shapes)
- **Minimum area filter**: Configurable threshold to ignore small artifacts
- **Hierarchy analysis**: Only considers outer contours (not holes)

Hatching parameters:
- **Spacing**: Distance between parallel hatch lines (in pixels before scaling to paper size)
- **Angle**: Direction of hatch lines (0° = horizontal, 90° = vertical, 45° = diagonal)
- **Pattern**: Single direction cross-hatch (can run twice with different angles for cross-hatching)

### Line Detection Algorithm

1. Convert image to grayscale
2. Apply Otsu's thresholding for binary conversion
3. Skeletonize to get thin, single-pixel lines
4. Extract contours and simplify to polylines with adaptive simplification:
   - Tiny features (<30px perimeter): 1000× less simplification for punctuation, arrows, fine details
   - Small features (<100px): 200× less simplification for small text and labels
   - Medium features (<300px): 50× less simplification for detailed geometry
   - Large features: 10× less simplification for efficiency
5. Filter lines shorter than minimum threshold (default 0.01mm)

### Path Optimization

Uses greedy nearest-neighbor algorithm:
1. Start from origin
2. Find nearest undrawn line endpoint
3. Draw line (possibly in reverse)
4. Repeat until all lines drawn

### Line Joining

Iteratively joins line segments when endpoints are within tolerance distance, reducing total pen lifts and improving efficiency.

## Examples

### Basic Conversion

Convert a blueprint with default ultra detail settings:
```bash
python blueprint2gcode.py floor_plan.jpg output.gcode
```

### Detail Level Presets

The tool defaults to **ultra detail** for maximum fidelity, capturing even punctuation and small arrows. You can adjust detail levels using these presets:

#### Ultra Detail (Default - Best for Fine Details and Small Text)
Maximum fidelity, captures punctuation, arrows, and finest features (0.01mm minimum).
```bash
# This is the default - no parameters needed
python blueprint2gcode.py input.jpg output.gcode

# Or explicitly:
python blueprint2gcode.py input.jpg output.gcode \
    --simplify-epsilon 0.000001 \
    --join-tolerance 0.02 \
    --min-line-length 0.01
```

#### Extreme Detail (Best for Scanned/Photographic Blueprints)
Very high fidelity with good balance (previous default).
```bash
python blueprint2gcode.py input.jpg output.gcode \
    --simplify-epsilon 0.000005 \
    --join-tolerance 0.05 \
    --min-line-length 0.05
```

#### High Detail (Best for Hand-Drawn Blueprints)
Excellent detail preservation with good performance balance.
```bash
python blueprint2gcode.py input.jpg output.gcode \
    --simplify-epsilon 0.0001 \
    --join-tolerance 0.15 \
    --min-line-length 0.3
```

#### Standard Detail (Best for Clean Vector-Style Images)
Optimized for programmatically generated or very clean line art.
```bash
python blueprint2gcode.py input.jpg output.gcode \
    --simplify-epsilon 0.0003 \
    --join-tolerance 0.2 \
    --min-line-length 0.5
```

#### Fast/Draft Mode (Best for Quick Previews)
Lower detail, faster processing, smaller G-code files.
```bash
python blueprint2gcode.py input.jpg output.gcode \
    --simplify-epsilon 0.001 \
    --join-tolerance 0.5 \
    --min-line-length 1.0
```

### Other Common Adjustments

Convert a blueprint to A3 size for larger output:
```bash
python blueprint2gcode.py floor_plan.jpg output.gcode --paper-size A3
```

Convert to A5 for compact notebook plotting:
```bash
python blueprint2gcode.py sketch.png output.gcode --paper-size A5
```

Convert with tighter margins:
```bash
python blueprint2gcode.py floor_plan.jpg output.gcode --margin 10.0
```

Higher drawing speed for simple drawings:
```bash
python blueprint2gcode.py simple_sketch.png output.gcode --feed-rate 2000
```

Custom Z-axis values for specific plotter:
```bash
python blueprint2gcode.py diagram.jpg output.gcode --z-up 5.0 --z-down -0.5
```

Fill solid black areas with cross-hatching:
```bash
# Basic solid area filling
python blueprint2gcode.py floor_plan.jpg output.gcode --fill-solid-areas

# Custom hatch pattern - dense horizontal lines
python blueprint2gcode.py floor_plan.jpg output.gcode \
    --fill-solid-areas \
    --hatch-spacing 0.5 \
    --hatch-angle 0

# Sparse diagonal hatching for large areas
python blueprint2gcode.py mechanical_part.jpg output.gcode \
    --fill-solid-areas \
    --hatch-spacing 3.0 \
    --hatch-angle 45

# Only fill large solid areas (ignore small artifacts)
python blueprint2gcode.py logo.png output.gcode \
    --fill-solid-areas \
    --min-solid-area 500
```

Combine paper size with detail level:
```bash
# Large A3 output with high detail
python blueprint2gcode.py blueprint.jpg output.gcode \
    --paper-size A3 \
    --simplify-epsilon 0.0001 \
    --join-tolerance 0.15
```

## Troubleshooting

**Solid black areas appearing as outlines**: Enable the `--fill-solid-areas` flag to detect and fill solid regions with cross-hatching instead of just outlining them.

**Hatching too dense/sparse**: Adjust `--hatch-spacing` (default 1.0 pixels). Use lower values (0.5) for denser fill, higher values (2.0-3.0) for lighter fill.

**Small artifacts being filled**: Increase `--min-solid-area` threshold (default 100 pixels) to only fill larger solid regions.

**Hatching not aligned properly**: Adjust `--hatch-angle` (0-360 degrees). Common values: 0° (horizontal), 45° (diagonal), 90° (vertical).

**Missing small text or fine details**: The default ultra detail settings should capture most features including punctuation and small arrows. For extremely fine features, ensure high input resolution (300+ DPI recommended).

**Output too large/slow to plot**: Switch to Extreme, High, Standard or Fast mode using the presets above, or increase `--simplify-epsilon` and `--min-line-length`.

**Lines not detected**: Try a higher resolution input image. The default is already at ultra detail (0.000001 epsilon).

**Too many small segments**: Use Extreme, High, Standard or Fast mode presets, or increase `--min-line-length`.

**Lines not joining**: Increase `--join-tolerance` (e.g., `--join-tolerance 0.05`, `0.2` or `0.5`).

**Lines joining that shouldn't**: Decrease `--join-tolerance` (already at 0.02mm for ultra detail).

**Better input image quality tips**:
- Scan blueprints at 300 DPI or higher
- Ensure high contrast between lines and background
- Clean up noise/artifacts in image editor before conversion
- For photographs, use edge detection or convert to line art first

## Testing

The repository includes comprehensive test infrastructure. All test scripts are located in the `tests/` directory and should be run from there.

### Integrated Test Harness (Recommended)

Run all tests including regular conversions and solid area filling with visualization:

```bash
cd tests
python3 test_harness_integrated.py
```

This runs 11 tests including:
- Regular blueprint tests (simple box, floor plan, circuit, gears)
- Solid area tests (with and without filling)
- Various hatch configurations

**Features:**
- ✅ Side-by-side visualization of input image and G-code output
- ✅ Comprehensive HTML report with all results
- ✅ Statistics for each test (lines, distance, time)
- ✅ Automatic test image generation if needed

**Outputs:**
- `test_visualizations_integrated/` - PNG visualizations for each test
- `test_output_integrated/` - Generated G-code files
- `test_visualizations_integrated/test_report.html` - Interactive HTML report

**View Results:**
```bash
# Display key results in a grid
python show_test_results.py

# Open HTML report in browser
xdg-open test_visualizations_integrated/test_report.html
```

### Testing Solid Area Filling

Generate solid area test images:

```bash
python generate_solid_test_images.py
```

This creates 8 test images in `../test_data/test_images_solid/`:
1. **test1_simple_shapes.png** - Basic solid circles, squares, triangles
2. **test2_mixed_solid_outline.png** - Mix of solid and outline elements
3. **test3_text_with_solids.png** - Text labels with solid highlighting
4. **test4_floor_plan_with_walls.png** - Floor plan with solid walls
5. **test5_mechanical_part.png** - Mechanical part with solid sections
6. **test6_logo_style.png** - Logo-style design with solid elements
7. **test7_circuit_with_pads.png** - Circuit diagram with solid pads
8. **test8_small_details.png** - Various sizes to test minimum area threshold

Run standalone solid area tests:

```bash
cd tests
python3 test_harness_solid.py
```

This runs 18+ test configurations including:
- Different hatch angles (0°, 45°, 90°, 135°)
- Different hatch spacing (dense, standard, sparse)
- Different minimum area thresholds
- Different paper sizes (A3, A4, A6)
- Comparison tests with/without filling

All outputs saved to `../test_data/test_output_solid/` directory.

## License

MIT License - feel free to use and modify as needed.
