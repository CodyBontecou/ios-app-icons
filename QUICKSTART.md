# Quick Start Guide

Get started with the iOS App Icon Generator in 3 simple steps!

## 1. Setup

```bash
./setup.sh
```

This will:
- Create a Python 3.13 virtual environment
- Install all dependencies
- Create a .env file from the template

## 2. Configure API Token

1. Get your Replicate API token from: https://replicate.com/account/api-tokens
2. Edit `.env` file and add your token:

```bash
REPLICATE_API_TOKEN=r8_your_token_here
```

## 3. Generate Icons

Activate the virtual environment:

```bash
source venv/bin/activate
```

Generate your first icon:

```bash
icon-gen generate --subject "happy cat"
```

This will:
- Generate 4 AI-powered variations
- Remove backgrounds automatically
- Apply iOS rounded corner masks
- Create all required iOS icon sizes
- Save everything to `output/happy_cat-{timestamp}/`

## Examples

### iOS Style (Default)
```bash
icon-gen generate --subject "mountain logo"
```

### Flat Minimalist Style
```bash
icon-gen generate --subject "coffee cup" --style flat --color "blue"
```

### Vector Illustration Style
```bash
icon-gen generate --subject "rocket ship" --style vector
```

### More Variations
```bash
icon-gen generate --subject "cute dog" --variations 8
```

### Higher Quality (More Steps)
```bash
icon-gen generate --subject "sunset" --steps 50 --guidance-scale 8.0
```

## Output Structure

```
output/
└── happy_cat-20260125_123456/
    ├── originals/              # AI-generated images
    │   ├── variant-1.png
    │   ├── variant-2.png
    │   └── ...
    ├── processed/              # All iOS sizes
    │   ├── variant-1/
    │   │   ├── AppIcon-1024.png
    │   │   ├── AppIcon-180.png
    │   │   └── ...
    │   └── variant-2/
    │       └── ...
    └── metadata.json           # Generation details
```

## Tips

1. **Be Specific**: "blue rocket ship with stars" works better than "rocket"
2. **Try Multiple Variations**: Generate 4-8 variations and pick the best
3. **Experiment with Styles**: Each style (ios, flat, vector) gives different results
4. **Cost**: ~$0.01-0.05 per generation on Replicate

## Commands

- `icon-gen --help` - Show all commands
- `icon-gen generate --help` - Show generation options
- `icon-gen info` - Show current configuration

## Troubleshooting

**Missing API Token:**
```
❌ REPLICATE_API_TOKEN not found
```
→ Add your token to the `.env` file

**First Run is Slow:**
The background removal model downloads ~200MB on first use. Subsequent runs are much faster.

## Next Steps

Check out the full [README.md](README.md) for:
- Detailed usage examples
- All configuration options
- Advanced features
- Cost information
