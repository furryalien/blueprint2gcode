# Testing Guide for blueprint2gcode

This document describes the testing framework, standards, and guidelines for the blueprint2gcode project. All contributors should follow these guidelines when adding new features or making changes.

## Table of Contents

- [Testing Philosophy](#testing-philosophy)
- [Test Organization](#test-organization)
- [Test Categories](#test-categories)
- [Running Tests](#running-tests)
- [Writing New Tests](#writing-new-tests)
- [Test Validation Criteria](#test-validation-criteria)
- [Continuous Integration](#continuous-integration)
- [Troubleshooting](#troubleshooting)

---

## Testing Philosophy

### Core Principles

1. **Comprehensive Coverage**: All features must have corresponding test cases
2. **Automated Validation**: Tests should run automatically with clear pass/fail results
3. **Visual Verification**: Tests should generate visualizations for manual inspection
4. **Performance Tracking**: Track execution time and output metrics
5. **Regression Prevention**: All bug fixes must include regression tests

### Test-Driven Development

- Write tests before implementing new features when possible
- Every bug fix should include a test that would have caught it
- Tests should be simple, focused, and maintainable
- Test data should be version controlled and well-documented

---

## Test Organization

### Directory Structure

```
tests/
├── regression_suite.py              # Master regression test suite
├── generate_test_images.py          # Generate standard test images
├── generate_solid_test_images.py    # Generate solid fill test images
├── generate_inverted_test_images.py # Generate inverted color test images
├── test_harness_*.py                # Individual test harnesses
├── analyze_*.py                     # Analysis utilities
├── debug_*.py                       # Debug utilities
└── visualize_*.py                   # Visualization utilities

test_data/
├── test_images/                     # Standard test input images
├── test_images_corners/             # Corner accuracy test images
├── test_images_solid/               # Solid fill test images
├── test_images_letters/             # Letter/character test images
├── test_images_inverted/            # Inverted color test images
├── test_output/                     # Generated G-code outputs
├── test_output_*/                   # Category-specific outputs
└── *.json, *.html                   # Test reports

visualizations/
├── test_visualizations/             # Standard test visualizations
├── test_visualizations_corners/     # Corner test visualizations
├── test_visualizations_solid/       # Solid fill visualizations
└── test_visualizations_*/           # Other visualization outputs
```

### File Naming Conventions

- **Test scripts**: `test_*.py` or `test_harness_*.py`
- **Test images**: `test<N>_<description>.png` (e.g., `test1_simple_box.png`)
- **Output files**: `test<N>_<description>_<params>.gcode`
- **Visualizations**: `<test_name>_<params>.png`
- **Reports**: `*_report.html`, `*_report.json`

---

## Test Categories

### 1. Basic Conversion Tests

**Purpose**: Verify core conversion functionality with standard geometric shapes

**Test Images**:
- Simple boxes and rectangles
- Floor plans with walls
- Circuit diagrams
- Mechanical drawings
- Complex blueprints

**Validation Criteria**:
- G-code is generated without errors
- All major shapes are captured
- Line endpoints are accurate
- No unexpected artifacts

**Example**:
```bash
python3 blueprint2gcode.py test_data/test_images/test1_simple_box.png output.gcode
```

### 2. Corner Accuracy Tests

**Purpose**: Ensure sharp corners and edges are preserved accurately

**Test Images**:
- Single squares (various sizes)
- Nested squares and rectangles
- Grid patterns
- Rotated shapes (diamonds)
- Parallelograms and trapezoids

**Validation Criteria**:
- Corners are sharp (not rounded)
- Nested shapes maintain proper boundaries
- No overflow beyond shape boundaries
- Proper handling of parent-child relationships

**Example**:
```bash
python3 blueprint2gcode.py test_data/test_images_corners/test1_square_300x300.png \
    output.gcode --fill-solid-areas
```

### 3. Solid Area Fill Tests

**Purpose**: Test hatching patterns for filled solid areas

**Test Images**:
- Simple solid shapes (circles, squares, triangles)
- Mixed solid and outline elements
- Complex shapes with holes
- Mechanical parts
- Floor plans with walls

**Parameters to Test**:
- `--hatch-angle`: 0°, 45°, 90°, custom angles
- `--hatch-spacing`: 0.5, 1.0, 1.5, 2.0, 3.0 mm
- `--min-solid-area`: 1, 10, 50, 100 sq mm
- `--crosshatch`: Enable crosshatch pattern

**Validation Criteria**:
- Hatch lines stay within boundaries
- Proper spacing between lines
- Correct angle of hatching
- Holes are not filled
- No overflow or underfill

**Example**:
```bash
python3 blueprint2gcode.py test_data/test_images_solid/test1_simple_shapes.png \
    output.gcode --fill-solid-areas --hatch-angle 45 --hatch-spacing 2.0
```

### 4. Letter and Character Tests

**Purpose**: Handle text characters including thin shapes

**Test Images**:
- Alphabetic characters (A-Z, a-z)
- Numbers (0-9)
- Special characters (-, _, !, @, etc.)
- Mixed text and graphics

**Special Cases**:
- Underscore (1 pixel tall horizontal line)
- Minus sign (thin horizontal line)
- Period (very small dot)
- Lowercase letters with descenders

**Validation Criteria**:
- All characters are detected
- Thin shapes (1px tall) are handled correctly
- Horizontal fill applied to underscores
- Small areas are not skipped

**Example**:
```bash
python3 blueprint2gcode.py test_data/test_images_letters/letters.jpg \
    output.gcode --fill-solid-areas --hatch-spacing 1.5 --min-solid-area 1
```

### 5. Color Inversion Tests

**Purpose**: Handle white-on-black or light-on-dark images

**Test Images**:
- White lines on black background
- White shapes on colored backgrounds
- Inverted blueprints
- Dark mode diagrams

**Validation Criteria**:
- Correct detection with `--invert-colors`
- All white elements captured
- Background ignored properly
- No false positives from noise

**Example**:
```bash
python3 blueprint2gcode.py test_data/test_images_inverted/white_on_black_simple_box.png \
    output.gcode --invert-colors
```

### 6. Paper Size Tests

**Purpose**: Verify correct scaling for different paper sizes

**Paper Sizes**:
- A4: 210 × 297 mm
- A5: 148 × 210 mm
- A6: 105 × 148 mm

**Validation Criteria**:
- Output fits within paper dimensions
- Proper scaling maintains aspect ratio
- Margins are respected
- Drawing stays within bounds

**Example**:
```bash
python3 blueprint2gcode.py test.png output.gcode --paper-size A6
```

### 7. Orientation Tests

**Purpose**: Test auto, landscape, and portrait orientations

**Orientations**:
- `auto`: Automatically choose best orientation
- `landscape`: Force landscape orientation
- `portrait`: Force portrait orientation

**Validation Criteria**:
- Auto mode selects correct orientation
- Forced orientations work correctly
- No clipping or overflow
- Optimal use of paper space

**Example**:
```bash
python3 blueprint2gcode.py test.png output.gcode --orientation landscape
```

### 8. Integration Tests

**Purpose**: Test combinations of features together

**Scenarios**:
- Solid fill + color inversion
- Multiple paper sizes + orientations
- Complex shapes + hatching patterns
- Real-world blueprints

**Validation Criteria**:
- Features work together without conflicts
- Performance is acceptable
- Output quality is maintained
- No unexpected interactions

---

## Running Tests

### Quick Start

Run the comprehensive regression suite:

```bash
cd tests
python3 regression_suite.py
```

This will:
1. Run all test categories
2. Generate G-code outputs
3. Create visualizations
4. Generate HTML and JSON reports

### Command-Line Options

```bash
# Run quick subset of tests (faster)
python3 regression_suite.py --quick

# Run only specific category
python3 regression_suite.py --category solid

# Skip visualization generation (faster)
python3 regression_suite.py --skip-viz

# Show detailed output
python3 regression_suite.py --verbose
```

### Individual Test Harnesses

Run specific test categories individually:

```bash
# Basic tests
python3 test_harness.py

# Corner accuracy tests
python3 test_harness_corners.py

# Solid fill tests
python3 test_harness_solid.py

# Integrated tests
python3 test_harness_integrated.py

# A6 paper size tests
python3 test_harness_a6.py

# All tests with multiple orientations
python3 test_harness_all.py

# Color inversion tests
python3 test_invert_colors.py
```

### Generate Test Images

If test images don't exist or need regeneration:

```bash
# Standard test images
python3 generate_test_images.py

# Solid fill test images
python3 generate_solid_test_images.py

# Inverted color test images
python3 generate_inverted_test_images.py
```

---

## Writing New Tests

### Step 1: Create Test Images

Add test images to the appropriate directory:
- Standard tests: `test_data/test_images/`
- Corner tests: `test_data/test_images_corners/`
- Solid fill: `test_data/test_images_solid/`
- Inverted: `test_data/test_images_inverted/`

Use the naming convention: `test<N>_<description>.png`

### Step 2: Add Test Configuration

Edit `regression_suite.py` and add your test to the appropriate category:

```python
TEST_CATEGORIES = {
    'your_category': {
        'name': 'Your Test Category',
        'description': 'Description of what this tests',
        'image_dir': 'test_images',
        'output_dir': 'test_output',
        'viz_dir': 'test_visualizations',
        'tests': [
            'test_new_feature.png',
            ('test_with_params.png', {'--hatch-angle': '45'}),
        ],
        'params': {'--fill-solid-areas': None}
    }
}
```

### Step 3: Define Validation Criteria

If your test requires special validation, add it to the `validate_gcode()` function:

```python
def validate_gcode(gcode_file: Path, expected_min_paths: int = 1) -> Tuple[bool, str]:
    # Add your validation logic
    if special_condition:
        return False, "Validation failed: reason"
    return True, "Valid"
```

### Step 4: Run and Verify

```bash
python3 regression_suite.py --category your_category --verbose
```

Review the generated visualization and report to ensure correctness.

### Step 5: Document

Add entry to this guide explaining:
- What the test validates
- Expected behavior
- Known limitations
- Example usage

---

## Test Validation Criteria

### Automatic Validation

All tests are automatically validated against these criteria:

1. **Output Creation**: G-code file must be created
2. **Non-Empty Output**: File size > 0 bytes
3. **Minimum Paths**: At least N drawing paths (configurable)
4. **Drawing Distance**: Total drawing distance > 1mm
5. **Valid G-code**: File can be parsed without errors

### Manual Validation

Some aspects require visual inspection:

1. **Geometric Accuracy**: Shapes match input image
2. **Corner Sharpness**: Corners are not rounded
3. **Fill Quality**: Hatching is even and complete
4. **Boundary Respect**: No overflow beyond shapes
5. **Aesthetic Quality**: Output looks clean and professional

### Performance Criteria

Tests should meet these performance targets:

- **Execution Time**: < 30 seconds per test (typical)
- **Memory Usage**: < 500MB for standard images
- **Output Size**: Reasonable G-code file size
- **Line Efficiency**: Minimize unnecessary moves

---

## Continuous Integration

### Pre-Commit Checks

Before committing code changes:

```bash
# Run quick tests
python3 regression_suite.py --quick

# Verify no failures
echo $?  # Should be 0
```

### Pull Request Requirements

All pull requests must:

1. Pass all existing tests
2. Include tests for new features
3. Include tests for bug fixes
4. Update documentation if needed
5. Include visualization samples

### Automated Testing

The regression suite supports automated CI/CD:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    cd tests
    python3 regression_suite.py --skip-viz
    
- name: Upload Test Reports
  uses: actions/upload-artifact@v2
  with:
    name: test-reports
    path: test_data/*.html
```

---

## Troubleshooting

### Common Issues

#### Test Image Not Found

```
Error: Input file not found: test_data/test_images/test1.png
```

**Solution**: Generate test images first:
```bash
python3 generate_test_images.py
```

#### Conversion Timeout

```
Error: Execution timeout (60s)
```

**Solution**: 
- Reduce image size or complexity
- Increase timeout in `regression_suite.py`
- Check for infinite loops in code

#### Validation Failed

```
Error: Validation failed: Too few paths: 0 < 1
```

**Solution**:
- Check input image has detectable features
- Verify correct parameters (e.g., `--invert-colors`)
- Review conversion output for errors

#### Visualization Failed

```
Warning: Visualization failed: <error>
```

**Solution**:
- Check matplotlib is installed
- Verify output directory is writable
- Review G-code file is valid

### Debug Mode

Enable verbose output for detailed debugging:

```bash
python3 regression_suite.py --verbose
```

This shows:
- Full command lines
- Conversion output
- Detailed error messages
- Execution timing

### Manual Testing

For debugging specific issues:

```bash
# Run conversion manually
python3 ../blueprint2gcode.py \
    ../test_data/test_images/test1_simple_box.png \
    ../test_data/test_output/debug.gcode \
    --fill-solid-areas

# Check output
head -50 ../test_data/test_output/debug.gcode

# Visualize manually
python3 visualize_solid_comparison.py
```

---

## Best Practices

### Test Image Design

1. **Clear Features**: Use distinct, easily identifiable shapes
2. **Appropriate Size**: 800-1200px for standard tests
3. **High Contrast**: Black on white or white on black
4. **Clean Lines**: No anti-aliasing artifacts
5. **Documented**: Include description in filename

### Test Case Design

1. **Single Focus**: Each test should validate one aspect
2. **Minimal**: Use simplest case that demonstrates the feature
3. **Comprehensive**: Cover edge cases and boundaries
4. **Reproducible**: Same inputs always produce same outputs
5. **Fast**: Keep execution time under 30 seconds

### Code Quality

1. **Type Hints**: Use type annotations for clarity
2. **Documentation**: Clear docstrings for all functions
3. **Error Handling**: Graceful handling of failures
4. **Logging**: Informative messages at appropriate levels
5. **Cleanup**: Remove temporary files after tests

### Version Control

1. **Test Data**: Commit test images to repository
2. **Generated Files**: Don't commit generated G-code or visualizations
3. **Reports**: Don't commit HTML/JSON reports
4. **Documentation**: Keep this guide updated with changes

---

## Test Metrics

### Coverage Goals

Target test coverage by feature area:

| Feature Area | Coverage Target | Current Status |
|--------------|----------------|----------------|
| Basic Conversion | 100% | ✓ Complete |
| Corner Accuracy | 100% | ✓ Complete |
| Solid Fill | 100% | ✓ Complete |
| Hatching Patterns | 95% | ✓ Complete |
| Color Inversion | 100% | ✓ Complete |
| Paper Sizes | 100% | ✓ Complete |
| Orientations | 100% | ✓ Complete |
| Letters/Characters | 100% | ✓ Complete |
| Edge Cases | 80% | ⚠ In Progress |

### Performance Baselines

Typical execution times (reference system):

| Test Category | Avg Time | Max Time | Images |
|--------------|----------|----------|--------|
| Basic | 3s | 8s | 5 |
| Corners | 4s | 10s | 5 |
| Solid Fill | 8s | 20s | 5 |
| Letters | 12s | 25s | 1 |
| Inverted | 3s | 8s | 3 |
| Paper Sizes | 4s | 10s | 3 |
| Orientations | 4s | 10s | 3 |
| **Total** | **5s** | **25s** | **25** |

---

## Future Enhancements

### Planned Test Additions

1. **Stress Tests**: Very large images, complex patterns
2. **Performance Benchmarks**: Automated performance tracking
3. **Quality Metrics**: Automated quality scoring
4. **Comparative Tests**: Before/after optimization comparisons
5. **Real-World Cases**: Actual blueprint samples

### Infrastructure Improvements

1. **Parallel Execution**: Run tests in parallel for speed
2. **Cloud Testing**: Run on multiple platforms/environments
3. **Visual Regression**: Automated visual difference detection
4. **Performance Tracking**: Historical performance database
5. **Interactive Reports**: Web-based interactive test explorer

---

## Contributing

### Adding New Test Categories

1. Document the feature being tested
2. Create representative test images
3. Add category to `TEST_CATEGORIES` in `regression_suite.py`
4. Define validation criteria
5. Update this guide
6. Submit pull request with test results

### Reporting Test Failures

When reporting test failures, include:

1. Test name and category
2. Full command used
3. Error message and stack trace
4. Input image (if not in repository)
5. Expected vs. actual behavior
6. Environment details (OS, Python version, dependencies)

### Improving Tests

Suggestions for test improvements are welcome:

1. More comprehensive coverage
2. Better validation criteria
3. Improved visualizations
4. Performance optimizations
5. Documentation clarifications

---

## References

- [WORKSPACE_STRUCTURE.md](WORKSPACE_STRUCTURE.md) - Project organization
- [spec.md](spec.md) - Project specification
- [SOLID_AREA_IMPLEMENTATION.md](SOLID_AREA_IMPLEMENTATION.md) - Fill feature details
- [README.md](../README.md) - User documentation

---

## Appendix: Test Data Specification

### Test Image Requirements

**Format**: PNG or JPG
**Color Mode**: RGB or Grayscale
**Bit Depth**: 8-bit per channel
**Size**: 800-1200px typical
**Content**: High contrast, clean lines

### G-code Output Format

**Standard**: RepRap/Marlin compatible
**Coordinates**: Absolute positioning
**Units**: Millimeters
**Pen Commands**: Z0 (down), Z3 (up)
**Feed Rate**: F3000 (50mm/s)

### Validation Thresholds

```python
VALIDATION_THRESHOLDS = {
    'min_paths': 1,           # Minimum number of drawing paths
    'min_distance': 1.0,      # Minimum drawing distance (mm)
    'max_time': 60.0,         # Maximum execution time (seconds)
    'max_file_size': 100*1024*1024,  # Maximum G-code size (100MB)
}
```

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-02  
**Maintained By**: blueprint2gcode Contributors
