#!/bin/bash
# Generate brick block variants for all logo files

echo "Generating brick block variants for all logos..."
echo ""

# Function to convert SVG to PNG and WebP
convert_to_raster() {
    local svg_file=$1
    local png_file=$2
    local webp_file=$3
    local width=$4
    
    echo "  Converting to PNG (${width}px)..."
    nix-shell -p "python3.withPackages(ps: [ ps.pillow ps.cairosvg ])" --run \
        "python3 -c \"import cairosvg; cairosvg.svg2png(url='$svg_file', write_to='$png_file', output_width=$width)\""
    
    echo "  Converting to WebP..."
    nix-shell -p "python3.withPackages(ps: [ ps.pillow ps.cairosvg ])" --run \
        "python3 -c \"from PIL import Image; import cairosvg; import io; png_data = cairosvg.svg2png(url='$svg_file', output_width=$width); img = Image.open(io.BytesIO(png_data)); img.save('$webp_file', 'WEBP', quality=95)\""
}

# Square logos (20 pixels wide for square format)
echo "=== Processing Square Logos ==="
for file in logo/square/svg/outlined/spy-square-*.svg; do
    basename=$(basename "$file" .svg)
    output_svg="logo/square/svg/outlined/brick/${basename}-brick.svg"
    output_png="logo/square/png/${basename}-brick.png"
    output_webp="logo/square/png/${basename}-brick.webp"
    
    echo "Processing: $basename"
    nix-shell -p "python3.withPackages(ps: [ ps.pillow ps.cairosvg ])" --run \
        "python3 brick_blockify.py '$file' '$output_svg' 20 24 20 auto"
    
    convert_to_raster "$output_svg" "$output_png" "$output_webp" 800
    echo ""
done

# Horizontal logos without subtitle (30 pixels wide for wider horizontal format)
# These use auto detection for adaptive brick sizing (1x, 2x, 3x, 4x)
echo "=== Processing Horizontal Logos (Full, no subtitle) ==="
for file in logo/horizontal/svg/outlined/spy-simple-*.svg; do
    basename=$(basename "$file" .svg)
    output_svg="logo/horizontal/svg/outlined/brick/${basename}-brick.svg"
    output_png="logo/horizontal/png/${basename}-brick.png"
    output_webp="logo/horizontal/png/${basename}-brick.webp"
    
    echo "Processing: $basename"
    nix-shell -p "python3.withPackages(ps: [ ps.pillow ps.cairosvg ])" --run \
        "python3 brick_blockify.py '$file' '$output_svg' 30 24 20 auto"
    
    convert_to_raster "$output_svg" "$output_png" "$output_webp" 1600
    echo ""
done

# Horizontal logos WITH subtitle (these need special handling)
# Use the brick_blockify_full.py script to preserve subtitle as vector
echo "=== Processing Horizontal Logos with Subtitle ==="
for file in logo/horizontal/svg/outlined/spy-full-*.svg; do
    basename=$(basename "$file" .svg)
    output_svg="logo/horizontal/svg/outlined/brick/${basename}-brick.svg"
    output_png="logo/horizontal/png/${basename}-brick.png"
    output_webp="logo/horizontal/png/${basename}-brick.webp"
    
    echo "Processing: $basename (subtitle preserved as vector)"
    nix-shell -p "python3.withPackages(ps: [ ps.pillow ps.cairosvg ])" --run \
        "python3 brick_blockify_full.py '$file' '$output_svg' 30 24 20"
    
    convert_to_raster "$output_svg" "$output_png" "$output_webp" 1600
    echo ""
done

echo "=== Complete! ==="
echo "Square brick logos saved to:"
echo "  - SVG: logo/square/svg/outlined/brick/"
echo "  - PNG/WebP: logo/square/png/"
echo "Horizontal brick logos saved to:"
echo "  - SVG: logo/horizontal/svg/outlined/brick/"
echo "  - PNG/WebP: logo/horizontal/png/"
