#!/bin/bash
# Generate brick block variants for all logo files

echo "Generating brick block variants for all logos..."
echo ""

# Square logos (20 pixels wide for square format)
echo "=== Processing Square Logos ==="
for file in logo/square/svg/outlined/spy-square-*.svg; do
    basename=$(basename "$file" .svg)
    output="logo/square/svg/outlined/brick/${basename}-brick.svg"
    echo "Processing: $basename"
    nix-shell -p "python3.withPackages(ps: [ ps.pillow ps.cairosvg ])" --run \
        "python3 brick_blockify.py '$file' '$output' 20 24 20 2x2"
    echo ""
done

# Horizontal logos without subtitle (30 pixels wide for wider horizontal format)
# These use 2x2 bricks for the full logo
echo "=== Processing Horizontal Logos (Full, no subtitle) ==="
for file in logo/horizontal/svg/outlined/spy-simple-*.svg; do
    basename=$(basename "$file" .svg)
    output="logo/horizontal/svg/outlined/brick/${basename}-brick.svg"
    echo "Processing: $basename"
    nix-shell -p "python3.withPackages(ps: [ ps.pillow ps.cairosvg ])" --run \
        "python3 brick_blockify.py '$file' '$output' 30 24 20 2x2"
    echo ""
done

# Horizontal logos WITH subtitle (these need special handling)
# For now, using same approach - TODO: handle subtitle separately
echo "=== Processing Horizontal Logos with Subtitle ==="
for file in logo/horizontal/svg/outlined/spy-full-*.svg; do
    basename=$(basename "$file" .svg)
    output="logo/horizontal/svg/outlined/brick/${basename}-brick.svg"
    echo "Processing: $basename (WARNING: subtitle will be blockified too)"
    nix-shell -p "python3.withPackages(ps: [ ps.pillow ps.cairosvg ])" --run \
        "python3 brick_blockify.py '$file' '$output' 30 24 20 2x2"
    echo ""
done

echo "=== Complete! ==="
echo "Square logos saved to: logo/square/svg/outlined/brick/"
echo "Horizontal logos saved to: logo/horizontal/svg/outlined/brick/"
