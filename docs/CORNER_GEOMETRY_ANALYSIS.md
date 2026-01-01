# Corner Geometry Analysis: Why Some Corners Get Zero Coverage

## The User's Question

> "Why can't lines in a single direction at 45 degrees be used to fill to the corners? It seems the lines could just continue to be spaced in the same manner and we would end up with shorter lines at 45 degree angles that continue to the corners."

**Answer: You're absolutely correct** in principle. The issue isn't that we *can't* generate those lines - it's that with diagonal angles and discrete pixel sampling, some corners are extremely difficult to detect.

## The Geometry

For a 600×600 square from (100,100) to (700,700) with 45° hatching:

###  Corner Analysis

Each corner has a different relationship to the hatch direction:

1. **Bottom-Left (100, 100)** and **Top-Right (700, 700)**:
   - Both lie on the line y = x + 0 (b=0)
   - This line runs diagonally through the entire square
   - **Result: Excellent coverage** (250+ lines within 5mm)

2. **Bottom-Right (700, 100)** and **Top-Left (100, 700)**:
   - Bottom-Right: line y = x - 600 (b=-600)
   - Top-Left: line y = x + 600 (b=+600)
   - These lines just barely clip the corners
   - **Result: Zero coverage**

## Why Zero Coverage?

The line through Bottom-Right corner (700, 100) has intercept b = -600.

With our 3.85px spacing, we generate a line at offset -425, which corresponds to:
- b ≈ -601

This line intersects:
- **Top edge** at x = 701 (outside the square!)
- **Right edge** at y = 99 (outside the square!)

The line **misses the corner by 1 pixel** in both directions!

### Visualization

```
    y=100 (top edge)
    ├─────────────┐
    │             │ x=700
    │          (701,99) ← Line passes here
    │             ↓
    │         (700,100) ← Actual corner
    │             │
```

## Why This Happens

1. **Discrete Sampling**: With 3.85px spacing between lines, we step from b=-605 to b=-601 to b=-597
2. **Pixel Boundaries**: The exact corner is at integer coordinates (700, 100)
3. **Geometric Reality**: A line with b=-601 passes through (701, 99), not (700, 100)
4. **Mask Detection**: Our mask only includes pixels where both x≤700 AND y≥100
5. **Result**: The line doesn't intersect our mask!

## Should We Expect Lines at All Corners?

**For rectangular shapes with 45° hatching:** No, not always!

Your intuition is correct that shorter and shorter lines *should* approach all corners. But there's a critical geometric constraint:

- Lines perpendicular to the hatch direction (at the "sharp" corners) can only be reached if a hatch line happens to pass through that exact pixel
- With fixed spacing, this is not guaranteed
- Even if we add a line at the "correct" offset, floating-point to pixel conversion can cause it to miss by 1 pixel

## The Real Solution

There are several valid approaches:

1. **Crosshatch** (current implementation): Add perpendicular set of lines
   - Pros: Guarantees all corners covered
   - Cons: Doubles line count and drawing time

2. **Force Corner Lines**: Explicitly generate lines through each corner
   - Calculate exact line parameters to pass through corner pixel
   - Adjust the line equation slightly to ensure intersection
   - More complex but maintains single-angle benefit

3. **Accept Geometric Limitation**: Document that single-angle hatching  
   - May miss sharp corners perpendicular to hatch direction
   - This is geometric reality, not a bug
   - Visual impact is minimal (corners still have nearby lines within ~5mm)

## Current Status

The codebase uses **crosshatch** to guarantee complete corner coverage. However, you've correctly identified that this is "overbuilt" for the geometric problem at hand.

For most practical purposes, having lines within 5mm of a corner is sufficient - the pen tip has physical width and the missing pixel or two at a sharp corner won't be visually apparent in the final drawing.

## Recommendation

Consider making crosshatch **optional**:
- Default: Single-angle (faster, simpler)
- Option `--crosshatch`: Enable perpendicular second pass for perfect corner coverage
- Document that single-angle may have ~1-2 pixel gaps at sharp corners perpendicular to hatch direction

This gives users the choice between:
- **Speed**: 50% faster with acceptable corner coverage
- **Perfection**: Complete coverage at all corners with 2× drawing time
