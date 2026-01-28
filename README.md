# iOS App Icon Generator

AI-powered CLI tool for generating iOS app icons using Stable Diffusion. Automatically creates icons in all required iOS sizes with optional background removal and rounded corner masking.

## Features

- 🎨 **AI-Powered Generation**: Uses Stable Diffusion via Replicate API
- 📱 **iOS-Ready**: Generates all required iOS app icon sizes
- 🎭 **Multiple Styles**: iOS, flat, and vector illustration styles
- 🔄 **Batch Processing**: Generate multiple variations at once
- ✂️ **Background Removal**: Optional automatic background removal with rembg
- 🔲 **iOS Masking**: Applies authentic iOS rounded corner masks
- 📦 **Optimized Output**: PNG compression for smaller file sizes

## Installation

1. **Clone the repository**:
```bash
cd /Users/codybontecou/dev/ios-app-icons
```

2. **Install the package**:
```bash
pip install -e .
```

3. **Set up your API token**:
```bash
cp .env.example .env
# Edit .env and add your Replicate API token
```

Get your Replicate API token from: https://replicate.com/account/api-tokens

## Quick Start

Generate iOS app icons:

```bash
icon-gen generate --subject "happy cat" --style ios --variations 4
```

This will:
1. Generate 4 AI-powered variations
2. Remove backgrounds
3. Apply iOS rounded corner masks
4. Create all iOS icon sizes (1024px down to 20px)
5. Save everything to `output/happy_cat-{timestamp}/`

## Usage

### Basic Generation

```bash
# Generate iOS-style icons
icon-gen generate --subject "mountain logo"

# Generate flat minimalist icons
icon-gen generate --subject "coffee cup" --style flat --color "blue"

# Generate vector illustrations
icon-gen generate --subject "rocket ship" --style vector
```

### Advanced Options

```bash
icon-gen generate \
  --subject "your subject" \
  --style ios \
  --variations 6 \
  --output-dir ./my-icons \
  --steps 40 \
  --guidance-scale 8.0
```

### Skip Post-Processing

```bash
# Only generate original images (no resizing/masking)
icon-gen generate --subject "cat" --no-process

# Generate without background removal
icon-gen generate --subject "cat" --no-remove-bg

# Generate without iOS rounded corners
icon-gen generate --subject "cat" --no-mask
```

### Configuration Info

```bash
# View current configuration
icon-gen info
```

## Command Reference

### `generate`

Generate AI-powered app icons.

**Options**:
- `--subject TEXT` (required): What to generate (e.g., "happy cat", "mountain logo")
- `--style [ios|flat|vector]`: Icon style (default: ios)
- `--variations INTEGER`: Number of variations (default: 4)
- `--color TEXT`: Background color for flat style
- `--no-process`: Skip post-processing
- `--no-mask`: Skip iOS rounded corner mask
- `--no-remove-bg`: Skip background removal
- `--output-dir PATH`: Custom output directory
- `--model TEXT`: Replicate model (advanced)
- `--steps INTEGER`: Inference steps (default: 30)
- `--guidance-scale FLOAT`: Guidance scale (default: 7.0)

### `info`

Show configuration and system information.

## Output Structure

```
output/
└── {subject}-{timestamp}/
    ├── originals/              # AI-generated source images
    │   ├── variant-1.png
    │   ├── variant-2.png
    │   ├── variant-3.png
    │   └── variant-4.png
    ├── processed/              # Processed icons in all sizes
    │   ├── variant-1/
    │   │   ├── AppIcon-1024.png
    │   │   ├── AppIcon-180.png
    │   │   ├── AppIcon-120.png
    │   │   └── ... (all iOS sizes)
    │   └── variant-2/
    │       └── ...
    └── metadata.json           # Generation parameters
```

## iOS Icon Sizes

The tool generates all required iOS app icon sizes:

- **1024×1024** - App Store
- **180×180** - iPhone @3x
- **120×120** - iPhone @2x
- **167×167** - iPad Pro @2x
- **152×152** - iPad @2x
- **76×76** - iPad @1x
- **60×60** - iPhone Spotlight
- **40×40** - Spotlight @2x
- **29×29** - Settings
- **20×20** - Notification

## Styles

### iOS Style
Modern, rounded app icon style with gradients and depth. Perfect for App Store submissions.

```bash
icon-gen generate --subject "your app concept" --style ios
```

### Flat Style
Minimalist flat design with solid colors. Great for simple, clean icons.

```bash
icon-gen generate --subject "your app concept" --style flat --color "purple"
```

### Vector Style
Vector illustration style with smooth curves and vibrant colors.

```bash
icon-gen generate --subject "your app concept" --style vector
```

## Tips for Best Results

1. **Be Specific**: "blue rocket ship with stars" works better than just "rocket"
2. **Use Style Keywords**: Include words like "modern", "minimalist", "colorful"
3. **Iterate**: Generate multiple variations and pick the best one
4. **Post-Process**: The default settings (background removal + iOS mask) work well for most cases
5. **Cost**: Each generation costs ~$0.01-0.05 on Replicate (depends on model and steps)

## Troubleshooting

### "REPLICATE_API_TOKEN not found"
- Copy `.env.example` to `.env`
- Add your API token from https://replicate.com/account/api-tokens

### First Run is Slow
- The `rembg` library downloads a ~200MB model on first use
- Subsequent runs will be much faster

### Generation Failed
- Check your Replicate account has credits
- Try the alternative model with `--model` flag
- Reduce `--steps` for faster (but lower quality) generation

## Development

```bash
# Install in development mode
pip install -e .

# Run from source
python -m icon_generator.cli generate --subject "test"
```

## Dependencies

- `replicate` - AI model API
- `pillow` - Image processing
- `rembg` - Background removal
- `click` - CLI framework
- `python-dotenv` - Environment variables
- `requests` - HTTP client

## License

MIT

## Credits

Built with:
- [Replicate](https://replicate.com/) - AI model hosting
- [Stable Diffusion](https://stability.ai/) - Image generation
- [rembg](https://github.com/danielgatis/rembg) - Background removal
