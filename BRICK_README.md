# Brick-Style Logo Generation

This directory contains tools to generate blocky "brick-style" versions of SPY logos, simulating stacked bricks viewed from the side.

## Features

- **Proper Brick Proportions**: Follows real LEGO dimensions (0.6" × 0.5" width × height)
  - 2×2 bricks: 24px wide × 20px high
  - 1×1 bricks: 12px wide × 20px high
  - Height-to-width ratio: 5:6 (not square cubes)

- **Adaptive Brick Sizing**: Automatically chooses between 1×1 and 2×2 bricks based on pixel patterns for optimal appearance

- **No Shading**: Uses only original logo RGB colors without any opacity variations or color manipulation

- **Hairline Borders**: 0.5px black borders at 30% opacity between bricks

- **Side View with Studs**: Bricks shown from side with studs visible on top (~15% of brick height)

## Usage

### Generate All Brick Variants

```bash
make brick
```

This will generate brick versions of all logos in the `brick/` subdirectories.

### Generate Specific Categories

```bash
make brick-square            # Only square logos
make brick-horizontal        # Only horizontal logos
```

### Test Different Brick Modes

```bash
make test-brick-1x1         # Test with only 1×1 bricks
make test-brick-2x2         # Test with only 2×2 bricks
make test-brick-auto        # Test with adaptive brick sizing (recommended)
```

### Clean Generated Files

```bash
make clean-brick
```

## Files

- `brick_blockify.py`: Main script for generating brick-style logos
- `brick_blockify_full.py`: Special handling for "full" logos with subtitles (WIP)
- `Makefile`: Build system with targets for all variants
- `generate_all_brick_variants.sh`: Bash script for batch generation (legacy)

## Technical Details

### Brick Dimensions

Real LEGO bricks have proportions of:
- Width: 0.6 inches
- Depth: 0.6 inches  
- Height: 0.5 inches

This gives a height-to-width ratio of **5:6** (not 1:1).

In pixels:
- 2×2 bricks: 24px × 20px (studs included in height)
- 1×1 bricks: 12px × 20px (same height as 2×2)

### Adaptive Brick Sizing

In `auto` mode (default), the algorithm:
1. Rasterizes the SVG to a low-resolution grid
2. Analyzes consecutive pixels with the same color
3. Places a 2×2 brick when 2+ consecutive pixels match
4. Places a 1×1 brick otherwise
5. Uses only original RGB colors (no opacity, no shading)

### Color Handling

**IMPORTANT**: The script uses ONLY the original RGB colors from the source image. No shading, no opacity variations, no color manipulation whatsoever. Any visible "shading" would be from the original artwork, not added by the script.

### Rendering Process

1. **Upscale**: SVG is rendered at 4× the target pixel size
2. **Downscale**: Nearest-neighbor resampling to target size (removes anti-aliasing)
3. **Analyze**: Determine brick placement and colors
4. **Generate**: Create SVG with brick elements

## Output Structure

```
logo/
├── square/
│   └── svg/
│       └── outlined/
│           ├── spy-square-*.svg (original)
│           └── brick/
│               └── spy-square-*-brick.svg (generated)
└── horizontal/
    └── svg/
        └── outlined/
            ├── spy-logo-horizontal-*.svg (original)
            └── brick/
                └── spy-logo-horizontal-*-brick.svg (generated)
```

## Requirements

The scripts require Python 3 with:
- PIL/Pillow (image processing)
- cairosvg (SVG rasterization)

These are provided via nix-shell in the Makefile targets.

## Known Limitations

1. **Subtitle Handling**: "Full" logos with subtitles currently blockify the entire image. Proper subtitle preservation (keeping subtitle as vector while blockifying only the title) is work in progress.

2. **Color Precision**: Colors are quantized to the nearest pixel in the low-resolution grid, which may slightly alter gradients or subtle color transitions in the original.

3. **Detail Loss**: By design, fine details are lost in the blockification process. This is intentional for the "brick" aesthetic.

## Examples

Input (outlined SVG) → Output (brick style):
- `spy-square-multicolor-lightbg.svg` → `spy-square-multicolor-lightbg-brick.svg` (20×20 pixels → ~400×400px output)
- `spy-logo-horizontal-outlined-black.svg` → `spy-logo-horizontal-outlined-black-brick.svg` (30px wide → ~720px wide output)

All examples use adaptive brick sizing for the best balance between 1×1 and 2×2 bricks.
