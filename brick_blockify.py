#!/usr/bin/env python3
"""
Post-process SVG logos to make them blocky/pixelated like stacked bricks.
"""

import sys
from PIL import Image, ImageDraw
import cairosvg
import io


def svg_to_image(svg_path, width=200):
    """Convert SVG to PIL Image without anti-aliasing."""
    with open(svg_path, 'rb') as f:
        svg_data = f.read()
    
    # Convert SVG to PNG at higher resolution first
    png_data = cairosvg.svg2png(bytestring=svg_data, output_width=width * 4)
    img = Image.open(io.BytesIO(png_data))
    
    # Downscale using nearest neighbor (no anti-aliasing)
    img = img.resize((width, int(width * img.height / img.width)), Image.NEAREST)
    
    return img


def create_brick_side_view(x, y, brick_width, brick_height, color, opacity=1.0, show_studs=True, brick_type="2x2"):
    """Create SVG elements for a brick from side view with studs on top.
    
    Real brick proportions: 0.6" × 0.6" × 0.5" (width × depth × height)
    Height is 5/6 of width. Studs on top are part of the height.
    
    brick_type: "1x1", "2x2", "3x3", or "4x4" - determines number of studs (1, 2, 3, or 4)
    """
    r, g, b = color
    
    # Use ONLY original color - absolutely NO opacity variations (no shading!)
    base_color = f"rgb({r},{g},{b})"
    border_color = "rgb(0,0,0)"  # Hairline black border
    
    elements = []
    
    # Brick proportions: studs are about 15% of brick height
    # The TOTAL brick height includes studs - they don't add to the height
    # ALWAYS show studs - they're part of the brick design
    stud_height = max(2, int(brick_height * 0.15))  # ~15% for studs
    body_height = brick_height - stud_height  # Body is the rest
    body_y = y + stud_height
    
    # Main brick body - ONLY base color, NO opacity variations!
    elements.append(f'  <rect x="{x}" y="{body_y}" width="{brick_width}" height="{body_height}" fill="{base_color}"/>')
    
    # Hairline borders (0.5px)
    # Top border
    elements.append(f'  <line x1="{x}" y1="{body_y}" x2="{x + brick_width}" y2="{body_y}" stroke="{border_color}" stroke-width="0.5" opacity="0.3"/>')
    # Bottom border
    elements.append(f'  <line x1="{x}" y1="{y + brick_height}" x2="{x + brick_width}" y2="{y + brick_height}" stroke="{border_color}" stroke-width="0.5" opacity="0.3"/>')
    # Left border
    elements.append(f'  <line x1="{x}" y1="{body_y}" x2="{x}" y2="{y + brick_height}" stroke="{border_color}" stroke-width="0.5" opacity="0.3"/>')
    # Right border
    elements.append(f'  <line x1="{x + brick_width}" y1="{body_y}" x2="{x + brick_width}" y2="{y + brick_height}" stroke="{border_color}" stroke-width="0.5" opacity="0.3"/>')
    
    # Studs on top - layout depends on brick type
    # Number of studs matches brick width: 1x1=1, 2x2=2, 3x3=3, 4x4=4
    # Studs are aligned on a 12px grid (1x brick width) for consistency
    stud_count = {"1x1": 1, "2x2": 2, "3x3": 3, "4x4": 4}.get(brick_type, 2)
    
    # 7px wide studs centered in 12px grid cells
    # Use the allocated stud_height (already calculated as 15% of brick_height)
    stud_width = 7
    
    # Position studs on 12px grid (aligned with 1x brick centers)
    # Each stud is centered in its 12px cell
    base_unit = 12  # Grid size (1x brick width)
    
    for i in range(stud_count):
        # Center stud in its 12px grid cell (12-7)/2 = 2.5px offset
        stud_x = x + base_unit * i + (base_unit - stud_width) / 2
        stud_y = y
        
        # Stud body - ONLY base color, NO opacity, SHARP corners (no rx)
        # Use stud_height (not override) to stay within allocated space
        elements.append(f'  <rect x="{stud_x}" y="{stud_y}" width="{stud_width}" height="{stud_height}" fill="{base_color}"/>')
        
        # Hairline border around stud - SHARP corners (no rx)
        elements.append(f'  <rect x="{stud_x}" y="{stud_y}" width="{stud_width}" height="{stud_height}" fill="none" stroke="{border_color}" stroke-width="0.5" opacity="0.2"/>')
    
    
    return elements


def colors_similar(color1, color2, tolerance=2):
    """Check if two RGB colors are similar within tolerance."""
    return all(abs(c1 - c2) <= tolerance for c1, c2 in zip(color1, color2))


def image_to_brick_svg(img, block_width=24, block_height=20, min_alpha=128, brick_type="auto"):
    """Convert PIL Image to brick-style blocky SVG with adaptive brick sizing.
    
    Args:
        block_width: Width for 2x2 bricks (1x1=12px, 2x2=24px, 3x3=36px, 4x4=48px)
        block_height: Height for all bricks (5/6 of block_width for proper ratio)
        brick_type: "auto" (adaptive 1x1/2x2/3x3/4x4), "1x1", "2x2", "3x3", or "4x4"
    """
    width, height = img.size
    
    # Convert to RGBA if not already
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Get pixel data
    pixels = img.load()
    
    # First pass: identify which pixels are opaque and their colors
    opaque_map = {}
    color_map = {}
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            opaque_map[(x, y)] = (a >= min_alpha)
            if a >= min_alpha:
                color_map[(x, y)] = (r, g, b, a)
    
    # Determine brick sizes adaptively if auto mode
    brick_sizes = {}  # (x, y) -> brick_width (12, 24, 36, or 48)
    if brick_type == "auto":
        prev_row_first_brick = None  # Track first brick size of previous row
        prev_row_bricks = {}  # Track all bricks in previous row: x_pos -> (length, color)
        
        for y in range(height):
            x = 0
            row_first_brick = None  # Track first brick of this row
            current_row_bricks = {}  # Track bricks in current row: x_pos -> (length, color)
            
            while x < width:
                if not opaque_map.get((x, y), False):
                    x += 1
                    continue
                
                base_color = color_map.get((x, y), (0, 0, 0, 0))[:3]
                
                # Count how many consecutive pixels of same color exist
                color_run_length = 0
                for i in range(width - x):
                    if (opaque_map.get((x + i, y), False) and 
                        color_map.get((x + i, y), (0, 0, 0, 0))[:3] == base_color):
                        color_run_length += 1
                    else:
                        break
                
                # Find all possible brick sizes at this position
                possible_lengths = []
                for length in [4, 3, 2, 1]:
                    if x + length - 1 < width:
                        # Check if all pixels in range have same color
                        all_same = all(
                            opaque_map.get((x + i, y), False) and 
                            color_map.get((x + i, y), (0, 0, 0, 0))[:3] == base_color
                            for i in range(length)
                        )
                        if all_same:
                            possible_lengths.append(length)
                
                if not possible_lengths:
                    x += 1
                    continue
                
                # Start with longest possible brick
                max_length = possible_lengths[0]
                
                # Check if there's a brick directly below at the same x position
                # Avoid stacking same-width same-color bricks when color run > 2
                if y > 0:
                    brick_below = prev_row_bricks.get(x)
                    if brick_below is not None:
                        brick_below_length, brick_below_color = brick_below
                        
                        # If colors match and color run > 2, avoid using same width
                        if (brick_below_color == base_color and 
                            color_run_length > 2 and 
                            max_length == brick_below_length and
                            len(possible_lengths) > 1):
                            # Use a different size to create offset pattern
                            alternative_lengths = [l for l in possible_lengths if l != max_length]
                            if alternative_lengths:
                                # Choose the longest alternative
                                max_length = alternative_lengths[0]
                
                # If this is the first brick of the row, try to vary from previous row
                if row_first_brick is None and prev_row_first_brick is not None:
                    # Prefer different size than previous row's first brick
                    preferred_lengths = [l for l in possible_lengths if l != prev_row_first_brick]
                    if preferred_lengths:
                        # Choose the longest preferred size (deterministic)
                        max_length = preferred_lengths[0]
                    else:
                        # Use longest available
                        max_length = possible_lengths[0]
                
                # Track first brick of this row
                if row_first_brick is None:
                    row_first_brick = max_length
                
                # Track this brick for next row's comparison
                current_row_bricks[x] = (max_length, base_color)
                
                # Place brick of detected size
                brick_w = max_length * (block_width // 2)
                brick_sizes[(x, y)] = brick_w
                
                # Mark other pixels as used
                for i in range(1, max_length):
                    brick_sizes[(x + i, y)] = 0
                
                x += max_length
            
            # Post-process the row to replace 2+1 and 1+2 patterns with 3-width bricks
            row_positions = sorted([pos for pos in current_row_bricks.keys()])
            i = 0
            while i < len(row_positions) - 1:
                x1 = row_positions[i]
                x2 = row_positions[i + 1]
                length1, color1 = current_row_bricks[x1]
                length2, color2 = current_row_bricks[x2]
                
                # Check if we have adjacent bricks of similar color forming 2+1 or 1+2
                if colors_similar(color1, color2) and x1 + length1 == x2:
                    if (length1 == 2 and length2 == 1) or (length1 == 1 and length2 == 2):
                        # Replace with a single 3-width brick using the first brick's color
                        brick_sizes[(x1, y)] = 3 * (block_width // 2)
                        brick_sizes[(x1 + 1, y)] = 0
                        brick_sizes[(x1 + 2, y)] = 0
                        
                        # Update current_row_bricks tracking
                        current_row_bricks[x1] = (3, color1)
                        del current_row_bricks[x2]
                        
                        # Update row_positions list
                        row_positions.pop(i + 1)
                        continue
                
                i += 1
            
            # Update tracking for next iteration
            if row_first_brick is not None:
                prev_row_first_brick = row_first_brick
            prev_row_bricks = current_row_bricks
    else:
        # Fixed brick size
        if brick_type == "1x1":
            # Simple case: every opaque pixel gets a 1x1 brick
            for y in range(height):
                for x in range(width):
                    if opaque_map.get((x, y), False):
                        brick_sizes[(x, y)] = block_width // 2
        else:  # brick_type == "2x2"
            # For 2x2 mode: try to place 2x2 bricks, fallback to 1x1
            for y in range(height):
                x = 0
                while x < width:
                    if not opaque_map.get((x, y), False):
                        x += 1
                        continue
                    
                    # Check if we can place a 2x2 brick (need 2 consecutive opaque pixels)
                    if x + 1 < width and opaque_map.get((x + 1, y), False):
                        # Place 2x2 brick
                        brick_sizes[(x, y)] = block_width
                        brick_sizes[(x + 1, y)] = 0  # Skip next pixel
                        x += 2
                    else:
                        # Not enough space for 2x2, use 1x1 brick
                        brick_sizes[(x, y)] = block_width // 2
                        x += 1
    
    # Calculate actual SVG dimensions
    # Width should be based on the maximum x-coordinate of any brick
    svg_width = width * (block_width // 2)  # Each pixel position takes half-width
    
    # Height: Calculate the inner dimensions after stud calculation
    # When we pass body_height to create_brick_side_view, it recalculates:
    # inner_stud = body_height * 0.15, inner_body = body_height - inner_stud
    stud_height = max(2, int(block_height * 0.15))
    body_height = block_height - stud_height
    
    # The actual rendered body size (what create_brick_side_view will use)
    inner_stud_height = max(2, int(body_height * 0.15))
    inner_body_height = body_height - inner_stud_height
    
    # Spacing: upper brick body sits on lower brick stud
    content_height = (height - 1) * inner_body_height + body_height
    
    # For square aspect ratio images (where width == height), make output square
    # by padding vertically and centering the content
    if width == height:
        svg_height = svg_width  # Make it square
        vertical_offset = (svg_height - content_height) // 2
    else:
        svg_height = content_height
        vertical_offset = 0
    
    svg_parts = [
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
        f'<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" ',
        '     xmlns="http://www.w3.org/2000/svg">',
        f'  <desc>Brick-style blocky version - {brick_type} bricks side view</desc>',
    ]
    
    # Calculate stud and body heights once
    stud_height = max(2, int(block_height * 0.15))
    body_height = block_height - stud_height
    
    # Process each pixel as a brick - DRAW FROM BOTTOM TO TOP (reverse y order)
    # This way upper bricks are drawn after (on top of) lower bricks, hiding studs below
    for y in range(height - 1, -1, -1):  # Start from bottom (highest y) to top (y=0)
        for x in range(width):
            brick_w = brick_sizes.get((x, y), 0)
            if brick_w == 0:
                continue
            
            r, g, b, a = color_map.get((x, y), (0, 0, 0, 0))
            
            # Calculate brick position based on pixel coordinates to preserve shape
            brick_x = x * (block_width // 2)  # Each pixel x-position is half-width unit
            
            # Y position: space bricks by inner_body_height so upper brick bodies
            # sit on top of lower brick studs, hiding them naturally
            # Add vertical_offset to center content in square outputs
            brick_y = y * inner_body_height + vertical_offset
            
            # All bricks show studs - they're always visible from the side view
            show_studs = True
            
            # Determine brick type based on width
            # brick_w can be: 12 (1x), 24 (2x), 36 (3x), or 48 (4x)
            if brick_w == block_width // 2:
                btype = "1x1"
            elif brick_w == block_width:
                btype = "2x2"
            elif brick_w == block_width * 3 // 2:
                btype = "3x3"
            elif brick_w == block_width * 2:
                btype = "4x4"
            else:
                btype = "2x2"  # Default fallback
            
            # Create brick from side view - NO SHADING, only original RGB color
            # Opacity is ignored - we use only opaque bricks
            # All bricks have studs for consistent appearance
            # Use body_height as brick total height (stud will be part of it)
            brick_elements = create_brick_side_view(
                brick_x, brick_y, brick_w, body_height,
                (r, g, b),
                show_studs=show_studs,
                brick_type=btype
            )
            
            svg_parts.extend(brick_elements)
    
    svg_parts.append('</svg>')
    
    return '\n'.join(svg_parts)


def blockify_svg(input_svg, output_svg, pixel_width=20, block_width=24, block_height=20, brick_type="auto"):
    """
    Main function to convert SVG to blocky brick style.
    
    Args:
        input_svg: Path to input SVG file
        output_svg: Path to output SVG file
        pixel_width: Width in "pixels" for the rasterization (lower = blockier)
        block_width: Width of 2x2 brick in output (default 24, will be halved for 1x1)
        block_height: Height of bricks (default 20, which is 5/6 of 24 for proper ratio)
        brick_type: "auto" (adaptive), "1x1", or "2x2" brick type
    """
    print(f"Converting {input_svg} to blocky brick style ({brick_type} bricks, side view)...")
    print(f"  Rasterizing to {pixel_width} pixels wide")
    print(f"  2x2 brick size: {block_width}×{block_height}px, 1x1 brick size: {block_width//2}×{block_height}px")
    
    # Convert SVG to low-res image
    img = svg_to_image(input_svg, width=pixel_width)
    print(f"  Image size: {img.size}")
    
    # Convert to brick-style SVG
    brick_svg = image_to_brick_svg(img, block_width=block_width, block_height=block_height, brick_type=brick_type)
    
    # Write output
    with open(output_svg, 'w') as f:
        f.write(brick_svg)
    
    print(f"  Saved to {output_svg}")
    # Calculate actual output dimensions with stacking overlap
    stud_height = max(2, int(block_height * 0.15))
    body_height = block_height - stud_height
    inner_stud_height = max(2, int(body_height * 0.15))
    inner_body_height = body_height - inner_stud_height
    output_width = img.width * (block_width // 2)
    content_height = (img.height - 1) * inner_body_height + body_height
    
    # Report actual dimensions (square if input was square)
    if img.width == img.height:
        output_height = output_width
        print(f"  Output size: {output_width}×{output_height} (square, content centered)")
    else:
        output_height = content_height
        print(f"  Output size: {output_width}×{output_height}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python brick_blockify.py <input.svg> <output.svg> [pixel_width] [block_width] [block_height] [brick_type]")
        print("  pixel_width: Width in pixels for rasterization (default: 20, lower = blockier)")
        print("  block_width: Width of 2x2 brick (default: 24, 1x1 is half)")
        print("  block_height: Height of bricks (default: 20, which is 5/6 of 24)")
        print("  brick_type: 'auto' (adaptive), '1x1', or '2x2' (default: auto)")
        print("")
        print("Note: Real brick proportions are 0.6\" × 0.5\" (width × height)")
        print("      So height = 5/6 of width. Default 24×20 maintains this ratio.")
        sys.exit(1)
    
    input_svg = sys.argv[1]
    output_svg = sys.argv[2]
    pixel_width = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    block_width = int(sys.argv[4]) if len(sys.argv) > 4 else 24
    block_height = int(sys.argv[5]) if len(sys.argv) > 5 else 20
    brick_type = sys.argv[6] if len(sys.argv) > 6 else "auto"
    
    blockify_svg(input_svg, output_svg, pixel_width, block_width, block_height, brick_type)
