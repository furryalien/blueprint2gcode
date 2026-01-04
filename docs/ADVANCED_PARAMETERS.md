# Advanced Configuration Parameters

This document describes the advanced configuration parameters added to `blueprint2gcode.py` for fine-tuning solid area detection, hatching quality, thresholding, and fine line detection.

## Solid Area Detection Parameters

### `--solidity-threshold` (default: 0.7)
Controls how "solid" a shape must be to be considered a filled area rather than an outline.

- **Range**: 0.0 - 1.0
- **Calculation**: Area / Convex Hull Area
- **Default**: 0.7 (70% solid)
- **Usage**:
  - **Lower values (0.5-0.6)**: More permissive, will fill more shapes (useful for irregular or angular shapes)
  - **Higher values (0.8-0.9)**: More strict, only fills very solid/compact shapes
  - **Recommended**: Start with default; lower if solid shapes aren't being detected

**Example**:
```bash
# More permissive detection for angular text
python blueprint2gcode.py input.jpg output.gcode \
    --fill-solid-areas \
    --solidity-threshold 0.6
```

### `--thin-shape-width` (default: 20 pixels)
Width threshold for detecting thin vertical shapes like "1", "i", "l", "|".

- **Range**: 5-50 pixels (typical)
- **Purpose**: Ensures thin characters are considered for filling even if their total area is small
- **Usage**:
  - **Smaller values (10-15)**: For small fonts or fine details
  - **Larger values (25-30)**: For large fonts or thick strokes
  - **Recommended**: Adjust based on your image's character size

### `--thin-shape-height` (default: 15 pixels)
Height threshold for detecting thin horizontal shapes like "-", "_".

- **Range**: 5-30 pixels (typical)
- **Purpose**: Ensures thin horizontal elements are considered for filling
- **Usage**: Similar to thin-shape-width, adjust based on feature size

**Example**:
```bash
# Detect smaller thin shapes (small font)
python blueprint2gcode.py small_text.jpg output.gcode \
    --fill-solid-areas \
    --thin-shape-width 12 \
    --thin-shape-height 8
```

## Hatching Quality Parameters

### `--hatch-quality` (default: medium)
Preset for hatching quality that affects sampling density and coverage.

**Presets**:

| Preset | Mask Samples | Dense Sampling Rate | Margin Multiplier | Extra Lines | Use Case |
|--------|--------------|---------------------|-------------------|-------------|----------|
| **low** | 200 | 3 samples/pixel | 1.5× | 1 | Fast preview, simple shapes |
| **medium** | 500 | 10 samples/pixel | 2.0× | 3 | Balanced quality/speed (default) |
| **high** | 1000 | 20 samples/pixel | 2.5× | 5 | Maximum coverage, complex shapes |

**Parameters affected**:
- **mask_sample_size**: Number of mask boundary points sampled to calculate hatch extent
- **dense_sampling_rate**: Samples per pixel when checking line-mask intersections (critical for corner coverage)
- **hatch_spacing_margin_multiplier**: How far beyond calculated extent to generate hatch lines
- **extra_hatch_lines**: Additional lines beyond calculated range for safety margin

**Example**:
```bash
# Maximum quality for complex mechanical parts
python blueprint2gcode.py mechanical.jpg output.gcode \
    --fill-solid-areas \
    --hatch-quality high

# Fast preview
python blueprint2gcode.py test.jpg preview.gcode \
    --fill-solid-areas \
    --hatch-quality low
```

## Thresholding Parameters

### `--threshold-method` (default: otsu)
Selects the method for converting grayscale to binary.

**Options**:
- **otsu**: Automatic threshold calculation using Otsu's method (default)
  - Analyzes histogram to find optimal threshold
  - Works well for most images with clear contrast
  - No manual tuning needed

- **manual**: Use fixed threshold value
  - Gives full control over threshold
  - Useful for faded, low-contrast, or unusual images
  - Requires tuning with `--manual-threshold`

### `--manual-threshold` (default: 127)
Threshold value when using manual thresholding.

- **Range**: 0-255
- **0**: Everything becomes black (not useful)
- **127**: Middle value (50% gray)
- **255**: Everything becomes white (not useful)

**Guidelines**:
- **Lower values (60-100)**: Detect faint/light lines
- **Medium values (120-150)**: Standard threshold for typical contrast
- **Higher values (180-220)**: Only detect very dark lines, ignore light artifacts

**Example**:
```bash
# Faded blueprint with light lines
python blueprint2gcode.py faded.jpg output.gcode \
    --threshold-method manual \
    --manual-threshold 90

# High contrast with noise - only capture dark lines
python blueprint2gcode.py noisy.jpg output.gcode \
    --threshold-method manual \
    --manual-threshold 180
```

## Fine Line Detection Parameters

### `--min-contour-points` (default: 2)
Minimum number of points in a contour to be considered a line.

- **Range**: 1-10 (typical)
- **Default**: 2 (minimum to form a line)
- **Usage**:
  - **Lower values (1-2)**: Capture single-pixel artifacts (may include noise)
  - **Higher values (3-5)**: Filter out tiny artifacts, only keep substantial lines
  - **Recommended**: Keep at 2 unless you have specific noise issues

**Example**:
```bash
# Filter out tiny noise artifacts
python blueprint2gcode.py noisy_scan.jpg output.gcode \
    --min-contour-points 4
```

### `--contour-approx-method` (default: simple)
Contour approximation method used during line detection.

**Options**:
- **simple**: Compress horizontal, vertical, and diagonal segments (default)
  - More efficient, smaller memory usage
  - Good for most cases
  - May slightly simplify very fine details

- **none**: Preserve all contour points
  - Maximum detail preservation
  - Captures every pixel of the contour
  - Larger memory usage, slower processing
  - Best for very fine lines and intricate details

**Example**:
```bash
# Maximum detail for circuit board traces
python blueprint2gcode.py circuit.jpg output.gcode \
    --contour-approx-method none \
    --simplify-epsilon 0.000001
```

## Initial Position Parameters

### `--initial-x` / `--initial-y` (default: 0.0, 0.0)
Starting position for pen and path optimization.

- **Units**: millimeters
- **Default**: (0, 0) - origin
- **Purpose**: 
  - Sets where the pen starts before drawing
  - Path optimizer uses this as the starting point to minimize travel
  - Pen returns to this position after drawing

**Use Cases**:
- Plotter has specific home position
- Want to start from center of work area
- Avoiding mechanical limits at origin

**Example**:
```bash
# Start from center of A4 page (portrait)
python blueprint2gcode.py input.jpg output.gcode \
    --initial-x 105.0 \
    --initial-y 148.5

# Start from safe position away from edge
python blueprint2gcode.py input.jpg output.gcode \
    --initial-x 20.0 \
    --initial-y 20.0
```

## Combined Usage Examples

### Ultra-detailed fine line drawing
```bash
python blueprint2gcode.py circuit.jpg output.gcode \
    --contour-approx-method none \
    --min-contour-points 2 \
    --simplify-epsilon 0.000001 \
    --min-line-length 0.01 \
    --threshold-method otsu
```

### Faded blueprint with solid filling
```bash
python blueprint2gcode.py faded_blueprint.jpg output.gcode \
    --threshold-method manual \
    --manual-threshold 85 \
    --fill-solid-areas \
    --solidity-threshold 0.6 \
    --hatch-quality high
```

### High-quality mechanical part
```bash
python blueprint2gcode.py mechanical.jpg output.gcode \
    --fill-solid-areas \
    --hatch-quality high \
    --hatch-spacing 1.0 \
    --hatch-angle 45 \
    --crosshatch \
    --solidity-threshold 0.65
```

### Small text with fine details
```bash
python blueprint2gcode.py small_text.jpg output.gcode \
    --fill-solid-areas \
    --thin-shape-width 10 \
    --thin-shape-height 8 \
    --solidity-threshold 0.5 \
    --contour-approx-method none
```

## Troubleshooting with Advanced Parameters

| Problem | Parameter to Adjust | Recommended Value |
|---------|-------------------|-------------------|
| Solid shapes not being filled | `--solidity-threshold` | 0.5-0.6 (lower) |
| Small characters ignored | `--thin-shape-width/height` | 10-15 (lower) |
| Gaps in hatching at corners | `--hatch-quality` | high |
| Faint lines not detected | `--threshold-method manual`<br>`--manual-threshold` | 70-100 (lower) |
| Too many noise artifacts | `--manual-threshold` | 160-200 (higher) |
| Fine details disappearing | `--contour-approx-method` | none |
| Tiny noise lines included | `--min-contour-points` | 3-5 (higher) |
| Path starts from wrong place | `--initial-x/y` | Your plotter's home position |

## Performance Considerations

**Memory/Speed Impact**:
- `--contour-approx-method none`: 2-5× more memory, 20-30% slower
- `--hatch-quality high`: 2× more processing time for hatching
- `--threshold-method manual` vs `otsu`: Negligible difference

**Quality Impact**:
- Most parameters have minimal impact on output quality for typical images
- Use higher quality settings only when needed for complex shapes or fine details
- Start with defaults and adjust based on visual inspection of output

## Version History

- **v1.0**: Added solidity-threshold, thin-shape parameters, hatch-quality presets
- **v1.0**: Added threshold-method and manual-threshold
- **v1.0**: Added min-contour-points and contour-approx-method
- **v1.0**: Added initial-x and initial-y position parameters
