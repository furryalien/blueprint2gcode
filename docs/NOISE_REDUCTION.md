# Noise Reduction Feature

## Overview

The noise reduction feature helps eliminate unwanted artifacts, speckles, and compression noise from input images before converting them to G-code. This is particularly useful for:

- **Scanned documents** with dust, dirt, or scanning artifacts
- **JPEG images** with compression artifacts and blocking
- **Photos** with sensor noise or grain
- **Downloaded images** with low quality or artifacts
- **Screenshots** with anti-aliasing artifacts

Without noise reduction, these artifacts can create thousands of tiny G-code segments representing pinpricks, dots, and very short lines that significantly increase file size and plotting time while degrading output quality.

## The Problem

When converting noisy images, the converter detects every small artifact as a feature to draw. This results in:

1. **Massive G-code files** - A simple image can generate 100,000+ lines instead of a few thousand
2. **Tiny "pinprick" lines** - Single-pixel or very short segments (< 0.1mm)
3. **Excessive pen movements** - Constant up/down movements for tiny features
4. **Slow plotting** - Hours of plotting time for what should take minutes
5. **Poor visual quality** - Random dots and artifacts that don't represent the actual image

### Example

A paisley bird image without noise reduction:
- **134,557 lines of G-code**
- Thousands of pinpricks and sub-millimeter segments
- Poor representation of the original image

With noise reduction enabled:
- **~5,000-10,000 lines** (estimated, depends on complexity)
- Clean, smooth lines representing actual features
- High-quality output matching the original intent

## How It Works

The noise reduction feature uses two complementary image processing techniques:

### 1. Gaussian Blur

**Purpose:** Reduces high-frequency noise before edge detection

**How it works:**
- Applies a Gaussian (bell-curve) weighted average to each pixel
- Smooths out random noise while preserving major edges
- Larger kernel = more smoothing, but may blur fine details

**When to use:**
- Images with random speckles or grain
- Photos with sensor noise
- Images with anti-aliasing artifacts

### 2. Morphological Operations

**Purpose:** Removes small isolated artifacts after thresholding

**How it works:**
- **Opening operation** (erosion → dilation):
  - Erosion removes small white blobs
  - Dilation restores the size of remaining features
  - Net effect: eliminates tiny artifacts while preserving larger features

**When to use:**
- Salt-and-pepper noise (random black/white pixels)
- Small dots and pinpricks
- JPEG compression blocks

## Usage

### Basic Command Line

Enable noise reduction with default settings:

```bash
python blueprint2gcode.py input.jpg output.gcode --enable-noise-reduction
```

### All Noise Reduction Parameters

```bash
python blueprint2gcode.py input.jpg output.gcode \
    --enable-noise-reduction \
    --gaussian-blur-kernel 5 \
    --morph-kernel-size 3 \
    --morph-iterations 1
```

### Parameter Reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--enable-noise-reduction` | flag | off | Enable noise reduction preprocessing |
| `--gaussian-blur-kernel` | int | 3 | Blur kernel size (odd number, 0=disable) |
| `--morph-kernel-size` | int | 2 | Morphological kernel size for artifact removal |
| `--morph-iterations` | int | 1 | Number of morphological iterations (higher=more aggressive) |

## Recommended Presets

### Mild Noise (Clean scans, high-quality images)

```bash
--enable-noise-reduction \
--gaussian-blur-kernel 3 \
--morph-kernel-size 2
```

**Use for:**
- Clean scanned documents
- High-quality digital images
- Images with minor compression artifacts

### Moderate Noise (Typical photos, web images)

```bash
--enable-noise-reduction \
--gaussian-blur-kernel 5 \
--morph-kernel-size 3
```

**Use for:**
- Standard JPEG photos
- Downloaded images from the web
- Screenshots with anti-aliasing
- Phone camera photos

### Heavy Noise (Dirty scans, low-quality images)

```bash
--enable-noise-reduction \
--gaussian-blur-kernel 7 \
--morph-kernel-size 4 \
--morph-iterations 2
```

**Use for:**
- Dirty or damaged scans
- Very low-quality JPEG images
- Images with significant grain or noise
- Old photocopies or faxes

## Combining with Other Parameters

For best results, combine noise reduction with appropriate line filtering:

```bash
python blueprint2gcode.py input.jpg output.gcode \
    --enable-noise-reduction \
    --gaussian-blur-kernel 5 \
    --morph-kernel-size 3 \
    --min-line-length 0.5 \
    --simplify-epsilon 0.1 \
    --join-tolerance 0.3
```

**Why these parameters work together:**

- **Noise reduction** removes artifacts before line detection
- **min-line-length** filters out remaining short segments
- **simplify-epsilon** smooths jagged edges into clean curves
- **join-tolerance** connects nearby endpoints into continuous paths

## Parameter Tuning Guide

### Gaussian Blur Kernel

**Values:** 0, 3, 5, 7, 9, 11, ... (must be odd)

- **0** = Disabled (no blur)
- **3** = Minimal blur, preserves fine details
- **5** = Standard blur, good for most images
- **7-9** = Strong blur, removes heavy noise but may lose fine details
- **11+** = Very aggressive, only for extremely noisy images

**Signs you need more blur:**
- Still seeing random dots in the output
- Many isolated single-pixel features

**Signs you have too much blur:**
- Fine details are missing
- Corners appear rounded
- Thin lines disappear

### Morphological Kernel Size

**Values:** 1, 2, 3, 4, 5, ...

- **1-2** = Minimal cleanup, preserves detail
- **3-4** = Standard cleanup, good for most noise
- **5+** = Aggressive cleanup, may remove wanted details

**Signs you need a larger kernel:**
- Small dots and artifacts remain
- Pinpricks still appearing in G-code

**Signs kernel is too large:**
- Thin lines disappearing
- Small features being removed
- Letters or fine details vanishing

### Morphological Iterations

**Values:** 1, 2, 3, ...

- **1** = Standard (recommended for most cases)
- **2** = More aggressive cleanup
- **3+** = Very aggressive (rarely needed)

**When to increase:**
- Stubborn noise persists after single iteration
- Very dense speckle patterns

**Warning:** More iterations = more aggressive removal of small features

## Technical Details

### Processing Pipeline

1. **Load image** → Convert to grayscale
2. **Invert colors** (if `--invert-colors` specified)
3. **Gaussian blur** (if noise reduction enabled and blur > 0)
4. **Threshold to binary** (Otsu or manual)
5. **Morphological opening** (if noise reduction enabled and kernel > 0)
6. **Contour detection** → Line extraction → G-code generation

### Why This Order Matters

- **Blur before threshold:** Reduces noise while preserving gray-level information
- **Morph after threshold:** Removes binary artifacts that survived thresholding
- **Two-stage approach:** Catches different types of noise

### Kernel Shapes

The implementation uses **elliptical kernels** for morphological operations:
- More natural than rectangular kernels
- Better preserves circular features
- Reduces directional bias

## Testing

### Unit Tests

Run the noise reduction test suite:

```bash
cd tests
python test_noise_reduction.py
```

This generates test images with various noise types and compares results with/without noise reduction.

### Regression Tests

Run noise reduction as part of the full regression suite:

```bash
cd tests
python regression_suite.py --category noise
```

Or include in full test run:

```bash
python regression_suite.py
```

## Troubleshooting

### Problem: G-code file still huge (100,000+ lines)

**Solutions:**
1. Increase blur kernel: `--gaussian-blur-kernel 7`
2. Increase morph kernel: `--morph-kernel-size 4`
3. Add line filtering: `--min-line-length 1.0`
4. Increase simplification: `--simplify-epsilon 0.2`

### Problem: Fine details are disappearing

**Solutions:**
1. Reduce blur kernel: `--gaussian-blur-kernel 3`
2. Reduce morph kernel: `--morph-kernel-size 2`
3. Use manual thresholding: `--threshold-method manual --manual-threshold 180`

### Problem: Some artifacts remain

**Solutions:**
1. Add a second morphological iteration: `--morph-iterations 2`
2. Increase blur kernel by 2: e.g., `5 → 7`
3. Combine with higher threshold: `--manual-threshold 200`

### Problem: Output looks "chunky" or blocky

**Solutions:**
1. Reduce morph kernel: `--morph-kernel-size 2`
2. Increase simplify-epsilon to smooth: `--simplify-epsilon 0.2`

## Performance Impact

Noise reduction adds minimal processing time:

- **Gaussian blur:** ~50-200ms depending on image size
- **Morphological operations:** ~50-150ms per iteration
- **Total overhead:** Usually < 500ms

This is negligible compared to the time saved from:
- Smaller G-code files (faster generation)
- Fewer line segments (faster path optimization)
- Shorter plotting time (fewer pen movements)

## Examples

### Example 1: Paisley Bird (User's Case)

**Original command:**
```bash
python blueprint2gcode.py chubby.paisley.bird.jpg output.gcode --paper-size A6
```
**Result:** 134,557 lines with pinpricks

**Fixed command:**
```bash
python blueprint2gcode.py chubby.paisley.bird.jpg output.gcode \
    --paper-size A6 \
    --enable-noise-reduction \
    --gaussian-blur-kernel 5 \
    --morph-kernel-size 3 \
    --min-line-length 0.5 \
    --simplify-epsilon 0.1
```
**Expected result:** ~5,000-15,000 lines, clean output

### Example 2: Scanned Document

```bash
python blueprint2gcode.py scanned_blueprint.png output.gcode \
    --enable-noise-reduction \
    --gaussian-blur-kernel 5 \
    --morph-kernel-size 3 \
    --manual-threshold 180 \
    --threshold-method manual
```

### Example 3: Low-Quality JPEG

```bash
python blueprint2gcode.py low_quality.jpg output.gcode \
    --enable-noise-reduction \
    --gaussian-blur-kernel 7 \
    --morph-kernel-size 4 \
    --morph-iterations 2 \
    --min-line-length 1.0
```

## See Also

- **ADVANCED_PARAMETERS.md** - Detailed parameter reference
- **TESTING_GUIDE.md** - Running the test suite
- **README.md** - General usage and examples
- **test_noise_reduction.py** - Unit test implementation

## Version History

- **v1.0** (2026-01-11) - Initial implementation with Gaussian blur and morphological operations
