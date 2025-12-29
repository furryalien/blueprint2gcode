# Blueprint to G-code Converter

Converts blueprint-style images (black lines on white background) to G-code for pen plotters and CNC machines with pen attachments.

## Features

- **Accurate line detection**: Uses skeletonization and contour detection for smooth line extraction
- **Adaptive simplification**: Preserves detail in small features like text while simplifying larger shapes
- **Path optimization**: Sophisticated nearest-neighbor algorithm minimizes pen travel
- **Line joining**: Automatically connects nearby line endpoints to reduce pen lifts
- **A4 output**: Scales images to fit A4 paper with configurable margins
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
python blueprint2gcode.py input.png output.gcode \
    --z-up 5.0 \
    --z-down 0.0 \
    --feed-rate 1500 \
    --margin 5.0 \
    --join-tolerance 1.0
```

## Command-Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--z-up` | 3.0 | Z position for pen up (mm) |
| `--z-down` | 0.0 | Z position for pen down (mm) |
| `--feed-rate` | 1000 | Drawing speed (mm/min) |
| `--travel-rate` | 3000 | Travel speed when pen is up (mm/min) |
| `--margin` | 1.0 | Margin around A4 page (mm) |
| `--join-tolerance` | 0.5 | Max distance to join line endpoints (mm) |
| `--min-line-length` | 0.5 | Minimum line length to include (mm) |
| `--simplify-epsilon` | 0.0003 | Line simplification factor (lower = more detail) |

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
   - Tiny features (<30px perimeter): 20x less simplification for maximum detail
   - Small features (<100px): 7x less simplification for fine text
   - Medium features (<300px): 2.5x less simplification
   - Large features: Normal simplification for efficiency

### Path Optimization

Uses greedy nearest-neighbor algorithm:
1. Start from origin
2. Find nearest undrawn line endpoint
3. Draw line (possibly in reverse)
4. Repeat until all lines drawn

### Line Joining

Iteratively joins line segments when endpoints are within tolerance distance, reducing total pen lifts and improving efficiency.

## Examples

Convert a blueprint with tighter margins:
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

## Troubleshooting
uses aggressive adaptive simplification that preserves detail in tiny features. For even more detail:
- Use higher resolution input images (recommended)
- Decrease `--simplify-epsilon` (e.g., `--simplify-epsilon 0.0001`)
- Decrease `--min-line-length` (e.g., `--min-line-length 0.2`)
- Increase `--simplify-epsilon` (e.g., `--simplify-epsilon 0.0003`)
- Increasing image contrast before conversion

**Lines not detected**: Try a higher resolution input image or adjust `--simplify-epsilon`

**Too many small segments**: Increase `--min-line-length` or `--simplify-epsilon`

**Lines not joining**: Increase `--join-tolerance`

**Output too detailed/slow**: Increase `--simplify-epsilon` slightly

## License

MIT License - feel free to use and modify as needed.
