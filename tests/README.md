# Tests Directory

This directory contains all test scripts, utilities, and test harnesses for the blueprint2gcode project.

## Quick Start

### Run All Tests (Comprehensive)

```bash
python3 regression_suite.py
```

This will run all test categories and generate a complete HTML report.

### Run Quick Tests (Faster)

```bash
python3 regression_suite.py --quick
```

Runs a subset of tests for rapid validation.

### Run Specific Category

```bash
python3 regression_suite.py --category solid
```

Available categories: `basic`, `corners`, `solid`, `letters`, `inverted`, `paper_sizes`, `orientations`

### View Test Report

After running tests, open the HTML report:

```bash
# Linux/Mac
xdg-open ../test_data/regression_test_report.html

# Or just navigate to:
test_data/regression_test_report.html
```

## Test Scripts

### Main Test Suite

- **`regression_suite.py`** - Comprehensive regression test suite (USE THIS!)
  - Runs all test categories
  - Generates visualizations
  - Creates HTML and JSON reports
  - Validates outputs automatically

### Test Image Generators

- **`generate_test_images.py`** - Generate standard test images
- **`generate_solid_test_images.py`** - Generate solid fill test images
- **`generate_inverted_test_images.py`** - Generate inverted color test images

Run these if test images are missing:
```bash
python3 generate_test_images.py
python3 generate_solid_test_images.py
python3 generate_inverted_test_images.py
```

### Individual Test Harnesses

These are older, category-specific test harnesses (mostly superseded by `regression_suite.py`):

- `test_harness.py` - Basic conversion tests
- `test_harness_corners.py` - Corner accuracy tests
- `test_harness_solid.py` - Solid fill tests
- `test_harness_integrated.py` - Integrated tests
- `test_harness_a6.py` - A6 paper size tests
- `test_harness_all.py` - All tests with multiple orientations
- `test_invert_colors.py` - Color inversion tests

### Debug and Analysis Tools

- `debug_*.py` - Various debug utilities
- `analyze_*.py` - Analysis scripts
- `visualize_*.py` - Visualization utilities
- `diagnose_*.py` - Diagnostic tools

## Test Categories

### 1. Basic Conversion
- Standard geometric shapes
- Floor plans
- Circuit diagrams
- Mechanical drawings

### 2. Corner Accuracy
- Sharp corners and edges
- Nested shapes
- Rotated objects
- Grid patterns

### 3. Solid Area Fill
- Hatching patterns
- Different angles and spacing
- Shapes with holes
- Complex mechanical parts

### 4. Letters and Characters
- Alphabetic characters
- Numbers and symbols
- Thin shapes (underscores)
- Mixed text and graphics

### 5. Color Inversion
- White-on-black images
- Light-on-dark diagrams
- Inverted blueprints

### 6. Paper Sizes
- A4 (210 × 297 mm)
- A5 (148 × 210 mm)
- A6 (105 × 148 mm)

### 7. Orientations
- Auto orientation
- Landscape mode
- Portrait mode

## File Organization

```
tests/
├── regression_suite.py           # ⭐ MAIN TEST SUITE
├── generate_*.py                 # Test image generators
├── test_harness_*.py            # Individual test harnesses
├── test_*.py                    # Specific test scripts
├── debug_*.py                   # Debug utilities
├── analyze_*.py                 # Analysis tools
├── visualize_*.py               # Visualization tools
└── README.md                    # This file

../test_data/
├── test_images/                 # Input test images
├── test_images_*/              # Category-specific inputs
├── test_output/                # Generated G-code
├── test_output_*/              # Category-specific outputs
└── regression_test_report.html # Test results report

../visualizations/
├── test_visualizations/        # Output visualizations
└── test_visualizations_*/      # Category-specific viz
```

## Common Commands

### Run all tests with full output
```bash
python3 regression_suite.py --verbose
```

### Run tests without visualizations (faster)
```bash
python3 regression_suite.py --skip-viz
```

### Run only solid fill tests
```bash
python3 regression_suite.py --category solid
```

### Generate missing test images
```bash
python3 generate_test_images.py
python3 generate_solid_test_images.py
```

### Run old-style test harness
```bash
python3 test_harness_integrated.py
```

## Interpreting Results

### Console Output

```
[1/5] Testing: test1_simple_box.png
  ✓ PASS (1.97s) - 3 paths, 1827.9mm
```

- ✓ PASS = Test passed all validation criteria
- ✗ FAIL = Test failed (see error message)
- Time = Execution time in seconds
- Paths = Number of drawing paths in output
- Distance = Total drawing distance in millimeters

### HTML Report

The HTML report includes:
- Summary statistics (total, passed, failed, success rate)
- Category breakdowns
- Individual test results with metrics
- Visual comparisons (input vs. output)
- Error details for failed tests

### JSON Report

Programmatic access to test results:
```bash
cat ../test_data/regression_test_report.json
```

Contains structured data for:
- Test execution times
- Pass/fail status
- G-code statistics
- Error messages

## Troubleshooting

### "Input file not found"
Run the image generators:
```bash
python3 generate_test_images.py
```

### "Conversion failed"
Run with verbose mode to see full error:
```bash
python3 regression_suite.py --verbose --category basic
```

### "Validation failed"
Check the G-code output manually:
```bash
head -50 ../test_data/test_output/test1_simple_box.gcode
```

### Tests are slow
Skip visualizations for faster execution:
```bash
python3 regression_suite.py --skip-viz
```

## Development Workflow

### Before committing changes:
```bash
# Run quick tests
python3 regression_suite.py --quick

# Or run full suite
python3 regression_suite.py
```

### When adding a new feature:
1. Add test images to appropriate directory
2. Add test configuration to `regression_suite.py`
3. Run tests to verify
4. Check HTML report for visual validation
5. Update documentation

### When fixing a bug:
1. Add test case that reproduces the bug
2. Fix the bug
3. Run regression suite to ensure fix works
4. Verify no other tests broke
5. Commit both fix and test

## Documentation

For complete testing guidelines, see:
- **[TESTING_GUIDE.md](../docs/TESTING_GUIDE.md)** - Comprehensive testing documentation
- **[WORKSPACE_STRUCTURE.md](../docs/WORKSPACE_STRUCTURE.md)** - Project organization
- **[spec.md](../docs/spec.md)** - Project specification

## Contributing

When contributing tests:
1. Follow existing naming conventions
2. Add clear descriptions and comments
3. Include both positive and negative test cases
4. Document expected behavior
5. Update this README if adding new categories

## Getting Help

- Review the [TESTING_GUIDE.md](../docs/TESTING_GUIDE.md) for detailed information
- Check existing test scripts for examples
- Run tests with `--verbose` for detailed output
- Examine the HTML test report for visual validation

---

**For full testing documentation, see [TESTING_GUIDE.md](../docs/TESTING_GUIDE.md)**
