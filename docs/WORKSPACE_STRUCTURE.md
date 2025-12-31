# Workspace Structure

This document describes the organized folder structure of the blueprint2gcode project.

## Directory Layout

```
blueprint2gcode/
├── blueprint2gcode.py          # Main conversion script
├── README.md                   # Project documentation
│
├── docs/                       # Documentation and specifications
│   ├── requirements.txt        # Python dependencies
│   ├── spec.md                 # Detailed project specification
│   ├── WORKSPACE_STRUCTURE.md  # This file
│   ├── BOUNDS_FIX.md          # Fix documentation
│   ├── CORNER_FIX_REPORT.md   # Fix documentation
│   ├── DIAGNOSIS_REPORT.md    # Fix documentation
│   ├── HATCHING_FIX.md        # Fix documentation
│   ├── INTEGRATION_SUMMARY.md # Fix documentation
│   ├── MECHANICAL_PART_FIX.md # Fix documentation
│   ├── SOLID_AREA_IMPLEMENTATION.md  # Implementation notes
│   └── SOLID_FILLING_QUICKSTART.md   # Quick start guide
│
├── tests/                      # All test scripts
│   ├── test_harness_*.py       # Various test harnesses
│   ├── generate_*.py           # Test image generators
│   ├── analyze_*.py            # Analysis scripts
│   ├── debug_*.py              # Debug utilities
│   ├── visualize_*.py          # Visualization scripts
│   └── __pycache__/            # Python bytecode cache
│
├── test_data/                  # Test inputs, outputs, and results
│   ├── test_images/            # Standard test input images
│   ├── test_images_corners/    # Corner accuracy test images
│   ├── test_images_solid/      # Solid area fill test images
│   ├── test_output/            # Standard test G-code outputs
│   ├── test_output_corners/    # Corner test outputs
│   ├── test_output_solid/      # Solid fill test outputs
│   ├── test_output_a6/         # A6 size test outputs
│   ├── test_output_a6_landscape/   # A6 landscape outputs
│   ├── test_output_a6_portrait/    # A6 portrait outputs
│   ├── test_output_all_auto/       # All tests auto orientation
│   ├── test_output_all_landscape/  # All tests landscape
│   ├── test_output_all_portrait/   # All tests portrait
│   ├── test_output_integrated/     # Integrated test outputs
│   ├── test_results*.json      # Test result data
│   ├── test_results*.html      # HTML test reports
│   └── *.gcode                 # Individual test G-code files
│
└── visualizations/             # Test visualization outputs
    ├── test_visualizations/            # Standard visualizations
    ├── test_visualizations_corners/    # Corner test visualizations
    ├── test_visualizations_solid/      # Solid fill visualizations
    ├── test_visualizations_a6/         # A6 size visualizations
    ├── test_visualizations_a6_landscape/
    ├── test_visualizations_a6_portrait/
    ├── test_visualizations_all_auto/
    ├── test_visualizations_all_landscape/
    ├── test_visualizations_all_portrait/
    ├── test_visualizations_integrated/
    └── *.png                   # Individual visualization images
```

## Path Conventions

All test scripts are located in the `tests/` directory and use relative paths to access other directories:

- **To access test images**: `../test_data/test_images/`
- **To access test outputs**: `../test_data/test_output/`
- **To access visualizations**: `../visualizations/test_visualizations/`
- **To access main script**: `../blueprint2gcode.py`
- **To access documentation**: `../docs/`

## Running Tests

All tests should be run from the `tests/` directory:

```bash
cd tests

# Generate test images
python3 generate_test_images.py
python3 generate_solid_test_images.py

# Run test harnesses
python3 test_harness_integrated.py
python3 test_harness_corners.py
python3 test_harness_solid.py
python3 test_harness_a6.py
python3 test_harness_all.py
```

## Main Script Usage

The main script should be run from the root directory:

```bash
cd /path/to/blueprint2gcode
python3 blueprint2gcode.py input.png output.gcode [options]
```

## File Organization

### Root Directory
Contains only the essential files:
- `blueprint2gcode.py` - The main conversion script
- `README.md` - User-facing documentation

### docs/
All documentation files including:
- Installation requirements
- Specifications
- Implementation notes
- Fix reports and summaries

### tests/
All test-related Python scripts including:
- Test harnesses for different scenarios
- Test image generators
- Analysis and debugging tools
- Visualization utilities

### test_data/
All test inputs and outputs:
- Test images (input)
- Generated G-code files (output)
- Test result data and reports

### visualizations/
All visualization outputs:
- Side-by-side comparisons of input/output
- Analysis visualizations
- Summary grids and reports

## Migration Notes

The workspace was reorganized from a flat structure to this organized layout. All test scripts were updated with relative paths to maintain functionality. The changes include:

1. Created four main subdirectories: `docs/`, `tests/`, `test_data/`, `visualizations/`
2. Moved 11 documentation files to `docs/`
3. Moved 21 test scripts to `tests/`
4. Moved all test data directories to `test_data/`
5. Moved all visualization directories to `visualizations/`
6. Updated all path references in test scripts to use relative paths
7. Updated README.md to reflect new structure

All functionality has been preserved and verified.
