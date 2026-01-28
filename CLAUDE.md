# iOS App Icon Generator

This repo generates AI-powered iOS app icons using Replicate's SDXL model.

## Quick Start

```bash
source venv/bin/activate
```

## Main Command

```bash
icon-gen generate \
  --subject "description of your app/icon" \
  --style custom \
  --custom-style "your artistic style description" \
  --variations 4 \
  --steps 40 \
  --guidance-scale 8.0
```

## Example: Anne Truitt Inspired Icon

```bash
icon-gen generate \
  --subject "health data export app with heart symbol" \
  --style custom \
  --custom-style "Anne Truitt inspired painted wooden columns, minimalist vertical forms, color field painting, deep purple and violet tones, smooth saturated color gradients, geometric stacked rectangles, contemplative aesthetic, matte painted surfaces" \
  --variations 4 \
  --steps 40 \
  --guidance-scale 8.5
```

## Available Styles

- `ios` - Standard iOS app icon style
- `flat` - Minimalist flat design
- `vector` - Vector illustration style
- `custom` - Full custom prompt (use with `--custom-style`)

## Output

Generated icons are saved to `output/{subject}-{timestamp}/`:
- `originals/` - Raw AI-generated 1024x1024 images
- `processed/` - All iOS sizes (1024, 180, 167, 152, 120, 76, 60, 40, 29, 20)

## Other Useful Commands

```bash
# Show current config
icon-gen info

# Skip post-processing
icon-gen generate --subject "cat" --style ios --no-process

# Use preset artistic styles
python style_gen.py judd
python style_gen.py -i  # interactive mode
```
