#!/usr/bin/env python3
"""
Process full logos with subtitles - blockify only the main title, keep subtitle as vector.
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
import subprocess
import tempfile
import re
import copy

def extract_title_and_subtitle(svg_path):
    """Extract title and subtitle portions from full logo.
    
    Returns:
        title_svg_path: Path to temporary SVG with just the title
        subtitle_elements: List of XML elements that form the subtitle
        original_viewbox: Original viewbox dimensions
        title_bottom_y: Y coordinate where title ends (subtitle starts)
    """
    tree = ET.parse(svg_path)
    root = tree.getroot()
    
    # Register namespace to preserve it
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    ET.register_namespace('sodipodi', 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd')
    ET.register_namespace('inkscape', 'http://www.inkscape.org/namespaces/inkscape')
    
    # Get viewBox
    viewbox = root.get('viewBox', '0 0 200 200').split()
    vb_x, vb_y, vb_w, vb_h = map(float, viewbox)
    
    # Find elements: typically the subtitle is a separate path or text element
    # Look for the text that contains subtitle (has aria-label with "Suomen")
    title_elements = []
    subtitle_elements = []
    other_elements = []
    
    for child in root:
        aria_label = child.get('aria-label', '')
        element_id = child.get('id', '')
        
        # Check if this is the subtitle (contains "Suomen" or "Palikka")
        if 'Suomen' in aria_label or 'Palikka' in aria_label:
            subtitle_elements.append(child)
        # Check if this is the title (SPY)
        elif aria_label == 'SPY' or element_id == 'text3':
            title_elements.append(child)
        # Other elements (defs, etc)
        elif child.tag.endswith('defs') or child.tag.endswith('namedview'):
            other_elements.append(child)
    
    # Determine subtitle start position
    # For SPY logos, the subtitle typically starts around 70% of the height
    title_height = vb_h * 0.70  # Top 70% is title
    title_bottom_y = vb_y + title_height
    
    # Create title-only SVG
    title_root = ET.Element(root.tag, root.attrib)
    title_root.set('viewBox', f'{vb_x} {vb_y} {vb_w} {title_height}')
    title_root.set('height', str(title_height))
    
    # Copy defs and other supporting elements
    for elem in other_elements:
        title_root.append(elem)
    
    # Copy title elements
    for elem in title_elements:
        title_root.append(elem)
    
    # Write title SVG to temp file
    temp_svg = tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False)
    tree = ET.ElementTree(title_root)
    tree.write(temp_svg.name, encoding='unicode', xml_declaration=True)
    temp_svg.close()
    
    return temp_svg.name, subtitle_elements, (vb_x, vb_y, vb_w, vb_h), title_bottom_y


def combine_brick_title_with_vector_subtitle(brick_svg, subtitle_elements, original_viewbox, title_bottom_y, output_svg):
    """Combine bricked title with original vector subtitle.
    
    Args:
        brick_svg: Path to the blockified title SVG
        subtitle_elements: List of XML elements containing the subtitle
        original_viewbox: Tuple of (x, y, width, height) from original SVG
        title_bottom_y: Y coordinate where subtitle should start
        output_svg: Path to save the combined result
    """
    # Parse brick SVG
    brick_tree = ET.parse(brick_svg)
    brick_root = brick_tree.getroot()
    
    # Register namespaces
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    ET.register_namespace('sodipodi', 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd')
    ET.register_namespace('inkscape', 'http://www.inkscape.org/namespaces/inkscape')
    
    # Get brick SVG dimensions
    brick_vb = brick_root.get('viewBox', '0 0 400 400').split()
    brick_x, brick_y, brick_w, brick_h = map(float, brick_vb)
    
    # Get original dimensions
    orig_x, orig_y, orig_w, orig_h = original_viewbox
    
    # Calculate scaling factor from original to brick
    scale = brick_w / orig_w
    
    # Calculate subtitle dimensions in original space
    subtitle_height_orig = orig_h - (title_bottom_y - orig_y)
    subtitle_height_scaled = subtitle_height_orig * scale
    
    # Create new combined SVG
    total_height = brick_h + subtitle_height_scaled
    
    new_root = ET.Element('{http://www.w3.org/2000/svg}svg')
    new_root.set('width', str(brick_w))
    new_root.set('height', str(total_height))
    new_root.set('viewBox', f'{brick_x} {brick_y} {brick_w} {total_height}')
    new_root.set('version', '1.1')
    
    # Copy defs from brick SVG if present
    for child in brick_root:
        if child.tag.endswith('defs'):
            new_root.append(copy.deepcopy(child))
    
    # Add brick title (all content from brick SVG except defs)
    for child in brick_root:
        if not child.tag.endswith('defs') and not child.tag.endswith('namedview'):
            new_root.append(copy.deepcopy(child))
    
    # Add subtitle with proper positioning and scaling
    if subtitle_elements:
        subtitle_group = ET.SubElement(new_root, '{http://www.w3.org/2000/svg}g')
        subtitle_group.set('id', 'vector-subtitle')
        
        # The subtitle starts at title_bottom_y in the original coordinate system
        # We need to scale it and position it so it appears right below the brick title
        # 
        # The brick title ends at y=brick_h in the new coordinate system
        # In the original, the subtitle region starts at y=title_bottom_y
        # We scale everything by 'scale' factor
        #
        # Transform: first scale, then translate to position below brick title
        # translate_y should move subtitle from its scaled position to below brick
        subtitle_group.set('transform', f'scale({scale}) translate(0, {(brick_h / scale) - title_bottom_y})')
        
        # Add subtitle elements
        for elem in subtitle_elements:
            subtitle_group.append(copy.deepcopy(elem))
    
    # Write output
    tree = ET.ElementTree(new_root)
    tree.write(output_svg, encoding='unicode', xml_declaration=True)
    
    print(f"  Combined brick title ({brick_w}×{brick_h}) with vector subtitle")


def process_full_logo(input_svg, output_svg, pixel_width=30, block_width=24, block_height=20):
    """Process a full logo: blockify title, keep subtitle as vector."""
    print(f"Processing full logo: {input_svg}")
    print("  Extracting title and subtitle...")
    
    # Extract title and subtitle
    title_svg, subtitle_elements, original_viewbox, title_bottom_y = extract_title_and_subtitle(input_svg)
    
    print(f"  Found {len(subtitle_elements)} subtitle element(s)")
    print("  Blockifying title...")
    
    # Blockify the title portion with auto brick sizing
    brick_title_svg = tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False).name
    
    cmd = [
        'python3', 'brick_blockify.py',
        title_svg, brick_title_svg,
        str(pixel_width), str(block_width), str(block_height), 'auto'
    ]
    
    subprocess.run(cmd, check=True)
    
    print("  Combining brick title with vector subtitle...")
    
    # Combine brick title with vector subtitle
    combine_brick_title_with_vector_subtitle(
        brick_title_svg, 
        subtitle_elements, 
        original_viewbox, 
        title_bottom_y, 
        output_svg
    )
    
    print(f"  Saved to {output_svg}")
    
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
