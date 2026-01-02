# Color Inversion Feature

## Overview
The `--invert-colors` feature allows blueprint2gcode to process images where the drawing is white/light colored on a dark background (inverted from the typical black-on-white blueprint style).

## Use Cases
- **White on Black**: Line drawings with white lines on black backgrounds
- **White on Blue**: Blueprint-style drawings with white/light lines on blue backgrounds
- **Any Inverted Image**: Any scenario where the subject lines are lighter than the background

## Usage

### Basic Usage
```bash
python blueprint2gcode.py input.png output.gcode --invert-colors
```

### With Additional Options
```bash
python blueprint2gcode.py input.png output.gcode --invert-colors --paper-size A4 --fill-solid-areas
```

## How It Works
The color inversion happens **before thresholding**:
1. Image is loaded and converted to grayscale
2. If `--invert-colors` is enabled, grayscale values are inverted (255 - pixel_value)
3. Otsu's automatic thresholding is applied to create binary image
4. Normal line detection and G-code generation proceeds

This approach ensures optimal thresholding results for inverted images.

## Test Images
Sample test images are provided in `test_data/test_images_inverted/`:
- `white_on_black_simple_box.png` - Simple box with lines
- `white_on_blue_circuit.png` - Circuit-style pattern on blue background
- `white_on_black_text.png` - Text-like shapes
- `white_on_black_geometric.png` - Various geometric shapes

## Testing

### Generate Test Images
```bash
python tests/generate_inverted_test_images.py
```

### Run Test Suite
```bash
python tests/test_invert_colors.py
```

## Performance Comparison

Example with `white_on_black_simple_box.png`:
- **With `--invert-colors`**: 5 lines, 765.51mm drawing distance ✓ Correct
- **Without `--invert-colors`**: 2 lines, 638.54mm drawing distance ✗ Missing detail

## Implementation Details
- **File Modified**: `blueprint2gcode.py`
- **Changes**:
  - Added `--invert-colors` CLI argument
  - Added inversion logic in `load_and_preprocess_image()` method
  - Updated docstrings to reflect dual support
- **Default**: Off (preserves backward compatibility)
- **Performance Impact**: Negligible (single numpy array operation)

## When to Use
Use `--invert-colors` when:
- Your source image has light/white lines on a dark background
- Processing scanned blueprints on blue paper
- Converting photos of whiteboards/chalkboards
- Working with negatives of standard blueprints

## When NOT to Use
Don't use `--invert-colors` when:
- Your image has standard black lines on white background
- Image is already correctly oriented (black is the drawing)
