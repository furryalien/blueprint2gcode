#!/usr/bin/env python3
"""
Display key test visualizations showing solid area filling results.
"""

import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path

def show_comparison_grid():
    """Display a grid of key test results."""
    viz_dir = Path('../visualizations/test_visualizations_integrated')
    
    # Key visualizations to show
    images = [
        ('solid_1_test1_simple_shapes.png', 'Without Fill\n5 lines, 969mm'),
        ('solid_2_test1_simple_shapes.png', 'With Fill\n816 lines, 33,152mm'),
        ('solid_4_test4_floor_plan_with_walls.png', 'Floor Plan Walls\n499 lines, 14,272mm'),
        ('solid_6_test7_circuit_with_pads.png', 'Circuit Pads\n485 lines, 28,558mm'),
    ]
    
    # Create 2x2 grid
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle('Blueprint2GCode - Integrated Test Results\nShowing Input Image (left) vs G-code Output (right)', 
                 fontsize=16, fontweight='bold')
    
    for idx, (img_file, title) in enumerate(images):
        row = idx // 2
        col = idx % 2
        ax = axes[row, col]
        
        img_path = viz_dir / img_file
        if img_path.exists():
            img = Image.open(img_path)
            ax.imshow(img)
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.axis('off')
        else:
            ax.text(0.5, 0.5, f'Image not found:\n{img_file}', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.axis('off')
    
    plt.tight_layout()
    
    # Save combined view
    output_file = viz_dir / 'combined_results.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Combined visualization saved to: {output_file}")
    
    # Show the plot
    plt.show()

if __name__ == '__main__':
    print("=" * 80)
    print("DISPLAYING KEY TEST RESULTS")
    print("=" * 80)
    show_comparison_grid()
