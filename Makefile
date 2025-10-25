# Makefile for SPY logo generation
# Generates outlined SVG and PNG versions from source SVG files

# Directories
HORIZONTAL_SVG_DIR = logo/horizontal/svg
HORIZONTAL_OUTLINED_DIR = logo/horizontal/svg/outlined
HORIZONTAL_PNG_DIR = logo/horizontal/png

SQUARE_SVG_DIR = logo/square/svg
SQUARE_OUTLINED_DIR = logo/square/svg/outlined
SQUARE_PNG_DIR = logo/square/png

# Find all source SVG files (excluding already outlined versions)
HORIZONTAL_SOURCE_SVGS = $(wildcard $(HORIZONTAL_SVG_DIR)/spy-*.svg)
HORIZONTAL_SOURCE_NAMES = $(notdir $(HORIZONTAL_SOURCE_SVGS))

SQUARE_SOURCE_SVGS = $(wildcard $(SQUARE_SVG_DIR)/spy-*.svg)
SQUARE_SOURCE_NAMES = $(notdir $(SQUARE_SOURCE_SVGS))

# Generate target file lists
HORIZONTAL_OUTLINED_SVGS = $(addprefix $(HORIZONTAL_OUTLINED_DIR)/, $(HORIZONTAL_SOURCE_NAMES))
HORIZONTAL_PNG_FILES = $(patsubst %.svg, $(HORIZONTAL_PNG_DIR)/%.png, $(HORIZONTAL_SOURCE_NAMES))
HORIZONTAL_WEBP_FILES = $(patsubst %.svg, $(HORIZONTAL_PNG_DIR)/%.webp, $(HORIZONTAL_SOURCE_NAMES))

SQUARE_OUTLINED_SVGS = $(addprefix $(SQUARE_OUTLINED_DIR)/, $(SQUARE_SOURCE_NAMES))
SQUARE_PNG_FILES = $(patsubst %.svg, $(SQUARE_PNG_DIR)/%.png, $(SQUARE_SOURCE_NAMES))
SQUARE_WEBP_FILES = $(patsubst %.svg, $(SQUARE_PNG_DIR)/%.webp, $(SQUARE_SOURCE_NAMES))

# Default target
.PHONY: all
all: outlined png webp brick

# Generate outlined SVG versions
.PHONY: outlined
outlined: $(HORIZONTAL_OUTLINED_SVGS) $(SQUARE_OUTLINED_SVGS)

$(HORIZONTAL_OUTLINED_DIR)/%.svg: $(HORIZONTAL_SVG_DIR)/%.svg
	@echo "Generating outlined version: $@"
	@mkdir -p $(HORIZONTAL_OUTLINED_DIR)
	@inkscape "$<" --export-text-to-path --export-filename="$@" 2>/dev/null || true
	@# Fix viewbox to match drawing area with padding
	@BOUNDS=$$(inkscape "$@" --query-all 2>/dev/null | grep '^svg' | cut -d, -f2-); \
	if [ -n "$$BOUNDS" ]; then \
		MARGIN=10; \
		X=$$(echo $$BOUNDS | cut -d, -f1); \
		Y=$$(echo $$BOUNDS | cut -d, -f2); \
		W=$$(echo $$BOUNDS | cut -d, -f3); \
		H=$$(echo $$BOUNDS | cut -d, -f4); \
		NX=$$(awk "BEGIN {print $$X - $$MARGIN}"); \
		NY=$$(awk "BEGIN {print $$Y - $$MARGIN}"); \
		NW=$$(awk "BEGIN {print $$W + 2 * $$MARGIN}"); \
		NH=$$(awk "BEGIN {print $$H + 2 * $$MARGIN}"); \
		sed -i "s/viewBox=\"[^\"]*\"/viewBox=\"$$NX $$NY $$NW $$NH\"/" "$@" 2>/dev/null || true; \
		sed -i "s/width=\"[^\"]*\"/width=\"$$NW\"/" "$@" 2>/dev/null || true; \
		sed -i "s/height=\"[^\"]*\"/height=\"$$NH\"/" "$@" 2>/dev/null || true; \
	fi

$(SQUARE_OUTLINED_DIR)/%.svg: $(SQUARE_SVG_DIR)/%.svg
	@echo "Generating outlined version: $@"
	@mkdir -p $(SQUARE_OUTLINED_DIR)
	@inkscape "$<" --export-text-to-path --export-filename="$@" 2>/dev/null || true
	@# Fix viewbox to match drawing area with padding
	@BOUNDS=$$(inkscape "$@" --query-all 2>/dev/null | grep '^svg' | cut -d, -f2-); \
	if [ -n "$$BOUNDS" ]; then \
		MARGIN=10; \
		X=$$(echo $$BOUNDS | cut -d, -f1); \
		Y=$$(echo $$BOUNDS | cut -d, -f2); \
		W=$$(echo $$BOUNDS | cut -d, -f3); \
		H=$$(echo $$BOUNDS | cut -d, -f4); \
		NX=$$(awk "BEGIN {print $$X - $$MARGIN}"); \
		NY=$$(awk "BEGIN {print $$Y - $$MARGIN}"); \
		NW=$$(awk "BEGIN {print $$W + 2 * $$MARGIN}"); \
		NH=$$(awk "BEGIN {print $$H + 2 * $$MARGIN}"); \
		sed -i "s/viewBox=\"[^\"]*\"/viewBox=\"$$NX $$NY $$NW $$NH\"/" "$@" 2>/dev/null || true; \
		sed -i "s/width=\"[^\"]*\"/width=\"$$NW\"/" "$@" 2>/dev/null || true; \
		sed -i "s/height=\"[^\"]*\"/height=\"$$NH\"/" "$@" 2>/dev/null || true; \
	fi
	@inkscape "$<" --export-text-to-path --export-filename="$@" 2>/dev/null || true

# Generate PNG versions from outlined SVGs with tight bounds
.PHONY: png
png: outlined $(HORIZONTAL_PNG_FILES) $(SQUARE_PNG_FILES)

$(HORIZONTAL_PNG_DIR)/%.png: $(HORIZONTAL_OUTLINED_DIR)/%.svg
	@echo "Generating PNG: $@"
	@mkdir -p $(HORIZONTAL_PNG_DIR)
	@inkscape "$<" --export-area-drawing --export-margin=10 --export-type=png --export-width=1600 --export-background-opacity=0 --export-filename="$@" 2>/dev/null || true

$(SQUARE_PNG_DIR)/%.png: $(SQUARE_OUTLINED_DIR)/%.svg
	@echo "Generating PNG: $@"
	@mkdir -p $(SQUARE_PNG_DIR)
	@inkscape "$<" --export-area-page --export-type=png --export-width=800 --export-background-opacity=0 --export-filename="$@" 2>/dev/null || true

# Generate WebP versions from PNG files
.PHONY: webp
webp: png $(HORIZONTAL_WEBP_FILES) $(SQUARE_WEBP_FILES)

$(HORIZONTAL_PNG_DIR)/%.webp: $(HORIZONTAL_PNG_DIR)/%.png
	@echo "Generating WebP: $@"
	@cwebp -q 95 "$<" -o "$@" 2>/dev/null || convert "$<" "$@" 2>/dev/null || true

$(SQUARE_PNG_DIR)/%.webp: $(SQUARE_PNG_DIR)/%.png
	@echo "Generating WebP: $@"
	@cwebp -q 95 "$<" -o "$@" 2>/dev/null || convert "$<" "$@" 2>/dev/null || true

# Clean generated files
.PHONY: clean
clean: clean-brick
	@echo "Cleaning generated files..."
	@rm -f $(HORIZONTAL_OUTLINED_SVGS)
	@rm -f $(HORIZONTAL_PNG_FILES)
	@rm -f $(HORIZONTAL_WEBP_FILES)
	@rm -f $(SQUARE_OUTLINED_SVGS)
	@rm -f $(SQUARE_PNG_FILES)
	@rm -f $(SQUARE_WEBP_FILES)

# Clean and rebuild everything
.PHONY: rebuild
rebuild: clean all

# Display help
.PHONY: help
help:
	@echo "SPY Logo Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  all              - Generate all outlined SVG, PNG and WebP files (default)"
	@echo "  outlined         - Generate outlined SVG files only"
	@echo "  png              - Generate PNG files (requires outlined SVGs)"
	@echo "  webp             - Generate WebP files (requires PNG files)"
	@echo "  brick            - Generate all brick-style variants (SVG, PNG, WebP)"
	@echo "  brick-square     - Generate square brick logos (SVG only)"
	@echo "  brick-horizontal - Generate horizontal brick logos (SVG only)"
	@echo "  clean            - Remove all generated files"
	@echo "  clean-brick      - Remove all brick-style generated files"
	@echo "  rebuild          - Clean and rebuild everything"
	@echo "  status           - Show file counts for generated assets"
	@echo "  help             - Show this help message"
	@echo ""
	@echo "Test targets:"
	@echo "  test-brick-1x1   - Test 1x1 brick mode on first square logo"
	@echo "  test-brick-2x2   - Test 2x2 brick mode on first square logo"
	@echo "  test-brick-auto  - Test auto brick mode on first square logo"
	@echo ""
	@echo "Horizontal logos:"
	@echo "  Source SVGs: $(HORIZONTAL_SVG_DIR)/spy-*.svg"
	@echo "  Outlined SVGs: $(HORIZONTAL_OUTLINED_DIR)/"
	@echo "  PNG files (1600px): $(HORIZONTAL_PNG_DIR)/"
	@echo "  WebP files (1600px): $(HORIZONTAL_PNG_DIR)/"
	@echo "  Brick variants: $(HORIZONTAL_BRICK_DIR)/"
	@echo ""
	@echo "Square logos:"
	@echo "  Source SVGs: $(SQUARE_SVG_DIR)/spy-*.svg"
	@echo "  Outlined SVGs: $(SQUARE_OUTLINED_DIR)/"
	@echo "  PNG files (800px): $(SQUARE_PNG_DIR)/"
	@echo "  WebP files (800px): $(SQUARE_PNG_DIR)/"
	@echo "  Brick variants: $(SQUARE_BRICK_DIR)/"

# Show status of generated files
.PHONY: status
status:
	@echo "Horizontal logos:"
	@echo "  Source SVG files: $(words $(HORIZONTAL_SOURCE_SVGS))"
	@echo "  Outlined SVG files: $(words $(wildcard $(HORIZONTAL_OUTLINED_DIR)/*.svg))"
	@echo "  PNG files: $(words $(wildcard $(HORIZONTAL_PNG_DIR)/*.png))"
	@echo "  WebP files: $(words $(wildcard $(HORIZONTAL_PNG_DIR)/*.webp))"
	@echo ""
	@echo "Square logos:"
	@echo "  Source SVG files: $(words $(SQUARE_SOURCE_SVGS))"
	@echo "  Outlined SVG files: $(words $(wildcard $(SQUARE_OUTLINED_DIR)/*.svg))"
	@echo "  PNG files: $(words $(wildcard $(SQUARE_PNG_DIR)/*.png))"
	@echo "  WebP files: $(words $(wildcard $(SQUARE_PNG_DIR)/*.webp))"

# ============================================================================
# BRICK-STYLE LOGO GENERATION
# ============================================================================
# Generates blocky/pixelated brick-style versions of outlined logos
# Brick dimensions follow real proportions: 0.6" × 0.5" (width × height)
#   - 2×2 bricks: 24px wide × 20px high
#   - 1×1 bricks: 12px wide × 20px high
#   - auto mode: Uses both sizes adaptively for optimal appearance

# Brick output directories
HORIZONTAL_BRICK_DIR = $(HORIZONTAL_OUTLINED_DIR)/brick
SQUARE_BRICK_DIR = $(SQUARE_OUTLINED_DIR)/brick

# Generate all brick logos (calls shell script for PNG/WebP generation too)
.PHONY: brick
brick: outlined
	@echo "Generating brick logo variants..."
	@bash generate_all_brick_variants.sh

# Clean brick variants
.PHONY: clean-brick
clean-brick:
	@echo "Cleaning brick variants..."
	@rm -f $(SQUARE_BRICK_DIR)/*-brick.svg
	@rm -f $(HORIZONTAL_BRICK_DIR)/*-brick.svg
	@rm -f $(SQUARE_PNG_DIR)/*-brick.png
	@rm -f $(SQUARE_PNG_DIR)/*-brick.webp
	@rm -f $(HORIZONTAL_PNG_DIR)/*-brick.png
	@rm -f $(HORIZONTAL_PNG_DIR)/*-brick.webp

# Generate only square brick logos (SVG only, no PNG/WebP)
.PHONY: brick-square
brick-square: outlined
	@echo "Generating square brick logos..."
	@mkdir -p $(SQUARE_BRICK_DIR)
	@for file in $(SQUARE_OUTLINED_DIR)/spy-square-*.svg; do \
		basename=$$(basename "$$file" .svg); \
		output="$(SQUARE_BRICK_DIR)/$${basename}-brick.svg"; \
		echo "Processing: $$basename"; \
		nix-shell -p "python3.withPackages(ps: [ ps.pillow ps.cairosvg ])" --run \
			"python3 brick_blockify.py '$$file' '$$output' 20 24 20 auto"; \
	done

# Generate only horizontal brick logos (SVG only, no PNG/WebP)
.PHONY: brick-horizontal
brick-horizontal: outlined
	@echo "Generating horizontal brick logos..."
	@mkdir -p $(HORIZONTAL_BRICK_DIR)
	@for file in $(HORIZONTAL_OUTLINED_DIR)/spy-simple-*.svg; do \
		basename=$$(basename "$$file" .svg); \
		output="$(HORIZONTAL_BRICK_DIR)/$${basename}-brick.svg"; \
		echo "Processing: $$basename"; \
		nix-shell -p "python3.withPackages(ps: [ ps.pillow ps.cairosvg ])" --run \
			"python3 brick_blockify.py '$$file' '$$output' 30 24 20 auto"; \
	done
	@for file in $(HORIZONTAL_OUTLINED_DIR)/spy-full-*.svg; do \
		basename=$$(basename "$$file" .svg); \
		output="$(HORIZONTAL_BRICK_DIR)/$${basename}-brick.svg"; \
		echo "Processing: $$basename (with subtitle)"; \
		nix-shell -p "python3.withPackages(ps: [ ps.pillow ps.cairosvg ])" --run \
			"python3 brick_blockify_full.py '$$file' '$$output' 30 24 20"; \
	done

# Test brick generation with different modes (square logos only)
.PHONY: test-brick-1x1
test-brick-1x1: outlined
	@echo "Testing 1x1 brick mode on first square logo..."
	@mkdir -p $(SQUARE_BRICK_DIR)
	@file=$$(ls $(SQUARE_OUTLINED_DIR)/spy-square-*.svg | head -n 1); \
	basename=$$(basename "$$file" .svg); \
	output="$(SQUARE_BRICK_DIR)/$${basename}-brick-test-1x1.svg"; \
	echo "Processing: $$basename (1x1 mode)"; \
	nix-shell -p "python3.withPackages(ps: [ ps.pillow ps.cairosvg ])" --run \
		"python3 brick_blockify.py '$$file' '$$output' 20 24 20 1x1"

.PHONY: test-brick-2x2
test-brick-2x2: outlined
	@echo "Testing 2x2 brick mode on first square logo..."
	@mkdir -p $(SQUARE_BRICK_DIR)
	@file=$$(ls $(SQUARE_OUTLINED_DIR)/spy-square-*.svg | head -n 1); \
	basename=$$(basename "$$file" .svg); \
	output="$(SQUARE_BRICK_DIR)/$${basename}-brick-test-2x2.svg"; \
	echo "Processing: $$basename (2x2 mode)"; \
	nix-shell -p "python3.withPackages(ps: [ ps.pillow ps.cairosvg ])" --run \
		"python3 brick_blockify.py '$$file' '$$output' 20 24 20 2x2"

.PHONY: test-brick-auto
test-brick-auto: outlined
	@echo "Testing auto brick mode on first square logo..."
	@mkdir -p $(SQUARE_BRICK_DIR)
	@file=$$(ls $(SQUARE_OUTLINED_DIR)/spy-square-*.svg | head -n 1); \
	basename=$$(basename "$$file" .svg); \
	output="$(SQUARE_BRICK_DIR)/$${basename}-brick-test-auto.svg"; \
	echo "Processing: $$basename (auto mode)"; \
	nix-shell -p "python3.withPackages(ps: [ ps.pillow ps.cairosvg ])" --run \
		"python3 brick_blockify.py '$$file' '$$output' 20 24 20 auto"
