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
all: outlined png webp

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
clean:
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
	@echo "  all      - Generate all outlined SVG, PNG and WebP files (default)"
	@echo "  outlined - Generate outlined SVG files only"
	@echo "  png      - Generate PNG files (requires outlined SVGs)"
	@echo "  webp     - Generate WebP files (requires PNG files)"
	@echo "  clean    - Remove all generated files"
	@echo "  rebuild  - Clean and rebuild everything"
	@echo "  help     - Show this help message"
	@echo ""
	@echo "Horizontal logos:"
	@echo "  Source SVGs: $(HORIZONTAL_SVG_DIR)/spy-*.svg"
	@echo "  Outlined SVGs: $(HORIZONTAL_OUTLINED_DIR)/"
	@echo "  PNG files (1600px): $(HORIZONTAL_PNG_DIR)/"
	@echo "  WebP files (1600px): $(HORIZONTAL_PNG_DIR)/"
	@echo ""
	@echo "Square logos:"
	@echo "  Source SVGs: $(SQUARE_SVG_DIR)/spy-*.svg"
	@echo "  Outlined SVGs: $(SQUARE_OUTLINED_DIR)/"
	@echo "  PNG files (800px): $(SQUARE_PNG_DIR)/"
	@echo "  WebP files (800px): $(SQUARE_PNG_DIR)/"

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
