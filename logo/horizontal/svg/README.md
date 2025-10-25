# SPY Logo Versions

This directory contains SVG logo files for SPY (Suomen Palikkayhteisö ry).

## Color Palette

From `colors.txt`:
- **Aqua**: #52d3d8
- **Light Blue**: #3887be  
- **Dark Purple**: #38419d
- **Very Dark Blue**: #200e3a
- **Bright Yellow**: #f2f597

## Logo Variants

### 1. Simple "SPY" Logos
Basic SPY text in various colors:
- `spy-simple-aqua.svg` - Aqua (#52d3d8)
- `spy-simple-lightblue.svg` - Light Blue (#3887be)
- `spy-simple-purple.svg` - Purple (#38419d)
- `spy-simple-black.svg` - Black
- `spy-simple-white.svg` - White
- `spy-simple-gradient.svg` - Gradient (Aqua → Light Blue → Purple)

### 2. "SPY ry" Logos
SPY with "ry" suffix:
- `spy-ry-aqua.svg` - Aqua
- `spy-ry-lightblue.svg` - Light Blue
- `spy-ry-purple.svg` - Purple
- `spy-ry-yellow.svg` - Bright Yellow
- `spy-ry-black.svg` - Black
- `spy-ry-white.svg` - White
- `spy-ry-gradient.svg` - Gradient (Aqua → Light Blue → Purple)

### 3. Full Logos with Subtitle
"SPY" with "Suomen Palikkayhteisö ry" below:

**With White Subtitle:**
- `spy-full-aqua-white.svg` - SPY in Aqua, subtitle white
- `spy-full-lightblue-white.svg` - SPY in Light Blue, subtitle white
- `spy-full-purple-white.svg` - SPY in Purple, subtitle white
- `spy-full-darkblue-white.svg` - SPY in Dark Blue, subtitle white
- `spy-full-gradient-white.svg` - SPY gradient, subtitle white
- `spy-full-white.svg` - Both in white

**With Black Subtitle:**
- `spy-full-aqua-black.svg` - SPY in Aqua, subtitle black
- `spy-full-lightblue-black.svg` - SPY in Light Blue, subtitle black
- `spy-full-purple-black.svg` - SPY in Purple, subtitle black
- `spy-full-darkblue-black.svg` - SPY in Dark Blue, subtitle black
- `spy-full-yellow-black.svg` - SPY in Yellow, subtitle black
- `spy-full-gradient-black.svg` - SPY gradient, subtitle black
- `spy-full-black.svg` - Both in black

## Typography

All logos use the **Outfit** font family from Google Fonts:
- SPY text: Outfit Extra Bold (weight 800), size 60px
- "ry" suffix: Outfit Bold (weight 700)
- Subtitle: Outfit Regular (weight 400), size 24px

## Usage Recommendations

### For Dark Backgrounds
Use logos with white subtitles or the gradient versions with white subtitle

### For Light Backgrounds  
Use logos with black subtitles or single-color versions

### Recommended Color Combinations
- **Aqua + White**: Fresh, modern look
- **Light Blue + White**: Professional, trustworthy
- **Purple + White**: Bold, creative
- **Gradient + White**: Dynamic, eye-catching (best for digital)

## File Specifications

- Format: SVG (Scalable Vector Graphics)
- Viewbox: 600x120 (full logos), 250x80 (ry logos), 200x80 (simple logos)
- All text uses web-safe fallback to sans-serif
- Font reference: `../../../fonts/Outfit-VariableFont_wght.ttf`

## Next Steps

To convert SVG text to paths (for universal compatibility):
```bash
cd svg
for file in *.svg; do
  inkscape "$file" --export-text-to-path --export-plain-svg --export-filename="../outlined/$file"
done
```

This will create path-based versions that don't require the font to be installed.
