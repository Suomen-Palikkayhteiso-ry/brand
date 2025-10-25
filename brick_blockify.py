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
    
    brick_type: "1x1" or "2x2" - determines number of studs (always 2 studs for consistency)
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
    # 1x1 brick: single stud (same width as 2x2 studs = 8px), 2x2 brick: two studs
    if brick_type == "1x1":
        # Single centered stud with same width as 2x2 brick studs (8px)
        stud_width = 8  # Fixed width to match 2x2 brick stud width
        stud_x = x + (brick_width - stud_width) // 2  # Center it
        stud_y = y
        
        # Stud body - ONLY base color, NO opacity, SHARP corners (no rx)
        elements.append(f'  <rect x="{stud_x}" y="{stud_y}" width="{stud_width}" height="{stud_height}" fill="{base_color}"/>')
        
        # Hairline border around stud - SHARP corners (no rx)
        elements.append(f'  <rect x="{stud_x}" y="{stud_y}" width="{stud_width}" height="{stud_height}" fill="none" stroke="{border_color}" stroke-width="0.5" opacity="0.2"/>')
    else:
        # Two studs for 2x2 brick
        stud_width = brick_width // 3
        stud_spacing = brick_width // 2
        
        for i in range(2):
            stud_x = x + (brick_width // 4) + (i * stud_spacing) - stud_width // 2
            stud_y = y
            
            # Stud body - ONLY base color, NO opacity, SHARP corners (no rx)
            elements.append(f'  <rect x="{stud_x}" y="{stud_y}" width="{stud_width}" height="{stud_height}" fill="{base_color}"/>')
            
            # Hairline border around stud - SHARP corners (no rx)
            elements.append(f'  <rect x="{stud_x}" y="{stud_y}" width="{stud_width}" height="{stud_height}" fill="none" stroke="{border_color}" stroke-width="0.5" opacity="0.2"/>')
    
    return elements


def image_to_brick_svg(img, block_width=24, block_height=20, min_alpha=128, brick_type="auto"):
    """Convert PIL Image to brick-style blocky SVG with adaptive brick sizing.
    
    Args:
        block_width: Width for 2x2 bricks (1x1 will be half)
        block_height: Height for all bricks (5/6 of block_width for proper ratio)
        brick_type: "auto" (adaptive 1x1/2x2), "1x1", or "2x2"
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
    brick_sizes = {}  # (x, y) -> brick_width (12 or 24)
    if brick_type == "auto":
        for y in range(height):
            x = 0
            while x < width:
                if not opaque_map.get((x, y), False):
                    x += 1
                    continue
                
                # Check if we can place a 2x2 brick (2 pixels wide)
                if x + 1 < width and opaque_map.get((x + 1, y), False):
                    # Check if colors are same/similar for 2 pixels
                    c1 = color_map.get((x, y))
                    c2 = color_map.get((x + 1, y))
                    if c1 and c2 and c1[:3] == c2[:3]:  # Same RGB color
                        brick_sizes[(x, y)] = block_width  # 2x2 brick
                        brick_sizes[(x + 1, y)] = 0  # Skip next pixel
                        x += 2
                    else:
                        brick_sizes[(x, y)] = block_width // 2  # 1x1 brick
                        x += 1
                else:
                    brick_sizes[(x, y)] = block_width // 2  # 1x1 brick
                    x += 1
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
    
    # Height: based on pixel grid y-coordinates using body_height for spacing
    stud_height = max(2, int(block_height * 0.15))
    body_height = block_height - stud_height
    
    # Maximum y-coordinate in pixels, plus one full brick height
    svg_height = height * body_height + stud_height
    
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
            
            # Y position: each row is spaced by body_height, so bricks stack on studs
            # This creates proper vertical stacking where upper bricks sit on lower brick studs
            brick_y = y * body_height
            
            # All bricks show studs - they're always visible from the side view
            show_studs = True
            
            # Determine brick type based on width
            btype = "1x1" if brick_w == block_width // 2 else "2x2"
            
            # Create brick from side view - NO SHADING, only original RGB color
            # Opacity is ignored - we use only opaque bricks
            # All bricks have studs for consistent appearance
            brick_elements = create_brick_side_view(
                brick_x, brick_y, brick_w, block_height,
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
    print(f"  Output size: {img.width * block_width}×{img.height * block_height}")


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
