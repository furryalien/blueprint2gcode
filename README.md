# Blueprint to G-code Converter

Converts blueprint-style images (black lines on white background) to G-code for pen plotters and CNC machines with pen attachments.

## Features

- **Accurate line detection**: Uses skeletonization and contour detection for smooth line extraction
- **Adaptive simplification**: Preserves detail in small features like text while simplifying larger shapes
- **Path optimization**: Sophisticated nearest-neighbor algorithm minimizes pen travel
- **Line joining**: Automatically connects nearby line endpoints to reduce pen lifts
- **Multiple paper sizes**: Supports A3, A4, A5, and A6 output formats
- **Auto-orientation**: Automatically chooses portrait or landscape based on image aspect ratio
- **Text-friendly**: Special handling for small text and fine details
- **Configurable**: Command-line options for all key parameters

## Installation

```bash
pip install -r requirements.txt
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
| `--join-tolerance` | 0.05 | Max distance to join line endpoints (mm) |
| `--min-line-length` | 0.05 | Minimum line length to include (mm) |
| `--simplify-epsilon` | 0.000005 | Line simplification factor (lower = more detail) |

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

### Line Detection Algorithm

1. Convert image to grayscale
2. Apply Otsu's thresholding for binary conversion
3. Skeletonize to get thin, single-pixel lines
4. Extract contours and simplify to polylines with adaptive simplification:
   - Tiny features (<30px perimeter): 500x less simplification for maximum detail
   - Small features (<100px): 100x less simplification for fine text
   - Medium features (<300px): 33x less simplification
   - Large features: 10x less simplification for efficiency

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

Convert a blueprint with default extreme detail settings:
```bash
python blueprint2gcode.py floor_plan.jpg output.gcode
```

### Detail Level Presets

The tool now defaults to **extreme detail** for maximum fidelity. You can adjust detail levels using these presets:

#### Extreme Detail (Default - Best for Scanned/Photographic Blueprints)
Maximum fidelity, captures finest curves and smallest features (0.05mm minimum).
```bash
# This is the default - no parameters needed
python blueprint2gcode.py input.jpg output.gcode

# Or explicitly:
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

Combine paper size with detail level:
```bash
# Large A3 output with high detail
python blueprint2gcode.py blueprint.jpg output.gcode \
    --paper-size A3 \
    --simplify-epsilon 0.0001 \
    --join-tolerance 0.15
```

## Troubleshooting

**Missing small text or fine details**: The default extreme detail settings should capture most features. For scanned documents with very fine text, ensure high input resolution (300+ DPI recommended).

**Output too large/slow to plot**: Switch to Standard or Fast mode using the presets above, or increase `--simplify-epsilon` and `--min-line-length`.

**Lines not detected**: Try a higher resolution input image or decrease `--simplify-epsilon` further.

**Too many small segments**: Use Standard or Fast mode presets, or increase `--min-line-length`.

**Lines not joining**: Increase `--join-tolerance` (e.g., `--join-tolerance 0.2` or `0.5`).

**Lines joining that shouldn't**: Decrease `--join-tolerance` (already at 0.05mm for extreme detail).

**Better input image quality tips**:
- Scan blueprints at 300 DPI or higher
- Ensure high contrast between lines and background
- Clean up noise/artifacts in image editor before conversion
- For photographs, use edge detection or convert to line art first

## License

MIT License - feel free to use and modify as needed.
