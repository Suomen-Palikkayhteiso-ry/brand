#!/usr/bin/env python3
"""
Process full logos with subtitles - blockify only the main title, keep subtitle as vector.
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
import subprocess
import tempfile

def extract_title_area(svg_path):
    """Extract the main title area from full logo (excluding subtitle)."""
    tree = ET.parse(svg_path)
    root = tree.getroot()
    
    # Parse SVG to find the subtitle text
    # For SPY full logos, the subtitle "Suomen Palikkayhteisö ry" is typically in the lower portion
    # We'll create a modified SVG with only the top portion (title)
    
    # Get viewBox
    viewbox = root.get('viewBox', '0 0 200 200').split()
    vb_x, vb_y, vb_w, vb_h = map(float, viewbox)
    
    # For full logos, assume subtitle is in bottom 25% of the image
    # Create a new SVG with only top 75%
    title_height = vb_h * 0.70  # Top 70% contains the main title
    
    # Create modified SVG
    new_root = ET.Element(root.tag, root.attrib)
    new_root.set('viewBox', f'{vb_x} {vb_y} {vb_w} {title_height}')
    new_root.set('height', str(title_height))
    
    # Copy all child elements
    for child in root:
        new_root.append(child)
    
    # Write to temp file
    temp_svg = tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False)
    tree = ET.ElementTree(new_root)
    tree.write(temp_svg.name, encoding='unicode', xml_declaration=True)
    temp_svg.close()
    
    return temp_svg.name, vb_h, title_height


def combine_brick_title_with_vector_subtitle(brick_svg, original_svg, output_svg):
    """Combine bricked title with original vector subtitle."""
    # Parse both SVGs
    brick_tree = ET.parse(brick_svg)
    brick_root = brick_tree.getroot()
    
    orig_tree = ET.parse(original_svg)
    orig_root = orig_tree.getroot()
    
    # Get original viewbox
    viewbox = orig_root.get('viewBox', '0 0 200 200').split()
    vb_x, vb_y, vb_w, vb_h = map(float, viewbox)
    
    # Get brick SVG dimensions
    brick_vb = brick_root.get('viewBox', '0 0 400 400').split()
    brick_w, brick_h = float(brick_vb[2]), float(brick_vb[3])
    
    # Create new combined SVG
    # Namespace handling
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    
    # Create root with full dimensions
    subtitle_start = vb_h * 0.70
    total_height = brick_h + (vb_h - subtitle_start)
    
    new_root = ET.Element('{http://www.w3.org/2000/svg}svg')
    new_root.set('width', str(brick_w))
    new_root.set('height', str(total_height))
    new_root.set('viewBox', f'0 0 {brick_w} {total_height}')
    new_root.set('xmlns', 'http://www.w3.org/2000/svg')
    
    # Add brick title (group)
    title_group = ET.SubElement(new_root, 'g')
    title_group.set('id', 'brick-title')
    for child in brick_root:
        if child.tag != '{http://www.w3.org/2000/svg}desc':
            title_group.append(child)
    
    # Add subtitle from original (scaled and positioned)
    subtitle_group = ET.SubElement(new_root, 'g')
    subtitle_group.set('id', 'vector-subtitle')
    scale_x = brick_w / vb_w
    scale_y = scale_x  # Maintain aspect ratio
    subtitle_group.set('transform', f'translate(0, {brick_h}) scale({scale_x}, {scale_y})')
    
    # Find and copy subtitle elements from original
    # Look for text or path elements in the lower portion
    for child in orig_root:
        # Copy elements that are in the subtitle area
        if child.tag.endswith('g') or child.tag.endswith('text') or child.tag.endswith('path'):
            # Simple heuristic: if it has a y attribute > 70% of height, it's probably subtitle
            y_attr = child.get('y', '')
            if y_attr:
                try:
                    y_val = float(y_attr)
                    if y_val > subtitle_start:
                        new_child = ET.SubElement(subtitle_group, child.tag, child.attrib)
                        new_child.text = child.text
                        new_child.tail = child.tail
                        for subchild in child:
                            new_child.append(subchild)
                except:
                    pass
    
    # Write output
    tree = ET.ElementTree(new_root)
    tree.write(output_svg, encoding='unicode', xml_declaration=True)


def process_full_logo(input_svg, output_svg, pixel_width=30, block_width=24, block_height=20):
    """Process a full logo: blockify title, keep subtitle as vector."""
    print(f"Processing full logo: {input_svg}")
    print("  Extracting title area...")
    
    # Extract title portion
    title_svg, orig_height, title_height = extract_title_area(input_svg)
    
    print(f"  Title area: {title_height}/{orig_height} of original")
    print("  Blockifying title...")
    
    # Blockify the title portion
    brick_title_svg = tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False).name
    
    cmd = [
        'python3', 'brick_blockify.py',
        title_svg, brick_title_svg,
        str(pixel_width), str(block_width), str(block_height), 'auto'
    ]
    
    subprocess.run(cmd, check=True)
    
    print("  Combining brick title with vector subtitle...")
    
    # For now, just use the bricked title
    # TODO: Properly combine with subtitle
    import shutil
    shutil.copy(brick_title_svg, output_svg)
    
    print(f"  Saved to {output_svg}")
    print("  NOTE: Subtitle handling is simplified - full combination not yet implemented")
    
    # Cleanup
    Path(title_svg).unlink()
    Path(brick_title_svg).unlink()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python brick_blockify_full.py <input.svg> <output.svg> [pixel_width] [block_width] [block_height]")
        print("  Processes 'full' logos: blockifies title, keeps subtitle as vector")
        sys.exit(1)
    
    input_svg = sys.argv[1]
    output_svg = sys.argv[2]
    pixel_width = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    block_width = int(sys.argv[4]) if len(sys.argv) > 4 else 24
    block_height = int(sys.argv[5]) if len(sys.argv) > 5 else 20
    
    process_full_logo(input_svg, output_svg, pixel_width, block_width, block_height)
