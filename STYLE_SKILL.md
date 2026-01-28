# Icon Style Generator Skill

Custom style-based icon generation skill for creating iOS app icons with any artistic style you can imagine.

## Features

- 🎨 **Custom Style Prompts** - Use any artistic style or aesthetic
- 🎯 **Preset Styles** - Quick access to curated artistic styles
- 🚀 **Easy to Use** - Simple command-line interface
- 🔄 **Interactive Mode** - Guided prompt building
- 📱 **iOS Ready** - Generates all required iOS icon sizes

## Quick Start

### Method 1: Direct Command (Easiest)

```bash
# Activate virtual environment
source venv/bin/activate

# Generate with built-in CLI
icon-gen generate \
  --subject "app icon" \
  --style custom \
  --custom-style "your artistic style here" \
  --variations 4
```

### Method 2: Style Generator Script (Recommended)

```bash
# Use preset styles
python style_gen.py judd
python style_gen.py deco
python style_gen.py pixel

# Use custom prompt
python style_gen.py "minimalist geometric art"

# Interactive mode
python style_gen.py -i
```

### Method 3: Shell Wrapper

```bash
./icon-style "your custom style prompt here"
```

## Available Preset Styles

The `style_gen.py` script includes these curated presets:

| Preset | Style | Description |
|--------|-------|-------------|
| `judd` | Donald Judd | Minimalist geometric stacked forms, aluminum and plexiglass |
| `deco` | Art Deco | 1920s geometric patterns, gold and black, elegant symmetry |
| `pixel` | Pixel Art | Retro gaming, 8-bit colors, nostalgic |
| `watercolor` | Watercolor | Soft brushstrokes, pastel colors, hand-painted feel |
| `neon` | Neon | Glowing edges, cyberpunk aesthetic, electric colors |
| `bauhaus` | Bauhaus | Geometric shapes, primary colors, modernist design |
| `memphis` | Memphis Design | 1980s postmodern, bright colors, playful shapes |
| `brutalism` | Brutalism | Raw concrete texture, bold geometric forms, stark minimalism |

## Usage Examples

### Using Presets

```bash
# Donald Judd inspired
python style_gen.py judd

# Art Deco style
python style_gen.py deco

# Pixel art
python style_gen.py pixel
```

### Custom Styles

```bash
# Isometric 3D
python style_gen.py "isometric 3D design, axonometric projection, clean edges"

# Japanese Minimalism
python style_gen.py "japanese minimalism, wabi-sabi, natural textures, zen aesthetic"

# Retro Futurism
python style_gen.py "retro futurism, 1960s space age, atomic era, vintage sci-fi"

# Organic Shapes
python style_gen.py "organic flowing shapes, biomorphic forms, nature inspired, smooth curves"
```

### Interactive Mode

```bash
python style_gen.py -i
```

This will guide you through:
1. Selecting a preset or entering custom prompt
2. Choosing the subject
3. Setting number of variations

### Advanced Options

```bash
# More variations
./icon-style "your style" -v 8

# Custom subject
./icon-style "your style" -s "photo sharing app"

# Higher quality (more steps)
./icon-style "your style" --steps 50

# Adjust guidance scale
./icon-style "your style" --guidance 10.0
```

## Direct CLI Usage

For complete control, use the `icon-gen` CLI directly:

```bash
icon-gen generate \
  --subject "photo sharing app" \
  --style custom \
  --custom-style "minimalist geometric stacked layers, translucent materials, modern design" \
  --variations 6 \
  --steps 40 \
  --guidance-scale 8.0
```

### CLI Options

- `--subject TEXT` - What to generate (e.g., "photo app", "health tracker")
- `--style custom` - Use custom style mode
- `--custom-style TEXT` - Your full style prompt (required for custom style)
- `--variations N` - Number of variations (default: 4)
- `--steps N` - Inference steps for quality (default: 30, recommend 40+)
- `--guidance-scale N` - Guidance scale (default: 7.0, recommend 8.0)
- `--no-process` - Skip post-processing (only generate originals)
- `--no-remove-bg` - Skip background removal
- `--no-mask` - Skip iOS rounded corner mask
- `--output-dir PATH` - Custom output directory

## Style Prompt Tips

### Good Prompts

✅ **Be specific about materials and aesthetics**
```
"brushed aluminum, translucent acrylic, industrial materials, geometric precision"
```

✅ **Reference art movements or artists**
```
"inspired by Piet Mondrian, primary colors, black grid lines, neoplasticism"
```

✅ **Combine multiple descriptors**
```
"flat design, vibrant gradients, long shadows, material design aesthetic"
```

✅ **Include technical details**
```
"isometric view, 45-degree angle, clean edges, vector style"
```

### What to Avoid

❌ Don't include "app icon" or "icon" (it's added automatically)
❌ Avoid vague terms like "cool" or "nice"
❌ Don't include text or letters in prompts
❌ Keep prompts focused on visual style, not function

## Examples Gallery

### Geometric & Minimalist

```bash
# Donald Judd
python style_gen.py "geometric stacked rectangles, aluminum plexiglass, industrial materials"

# Swiss Design
python style_gen.py "swiss design, grid system, helvetica, red and white, clean typography"

# Suprematism
python style_gen.py "suprematist composition, geometric shapes, black red white, Kazimir Malevich"
```

### Artistic Styles

```bash
# Impressionism
python style_gen.py "impressionist painting, loose brushstrokes, light and color, plein air"

# Pop Art
python style_gen.py "pop art, bold colors, halftone dots, Roy Lichtenstein, comic style"

# Art Nouveau
python style_gen.py "art nouveau, flowing organic lines, botanical motifs, elegant curves"
```

### Modern Design

```bash
# Glassmorphism
python style_gen.py "glassmorphism, frosted glass, blur effect, translucent layers, depth"

# Neumorphism
python style_gen.py "neumorphism, soft shadows, subtle highlights, monochromatic, tactile"

# Claymorphism
python style_gen.py "claymorphism, 3D clay render, soft shadows, playful, matte finish"
```

### Cultural & Historical

```bash
# Japanese
python style_gen.py "japanese minimalism, ma negative space, natural materials, wabi-sabi"

# Scandinavian
python style_gen.py "scandinavian design, light wood, white space, hygge, functional beauty"

# Industrial Revolution
python style_gen.py "industrial revolution, brass gears, mechanical parts, steampunk aesthetic"
```

## Output Structure

```
output/
└── {sanitized_prompt}-{timestamp}/
    ├── originals/              # AI-generated source images
    │   ├── variant-1.png
    │   ├── variant-2.png
    │   ├── variant-3.png
    │   └── variant-4.png
    ├── processed/              # All iOS sizes
    │   ├── variant-1/
    │   │   ├── AppIcon-1024.png
    │   │   ├── AppIcon-180.png
    │   │   └── ... (all sizes)
    │   └── variant-2/
    │       └── ...
    └── metadata.json           # Generation parameters
```

## Workflow

1. **Generate variations** with your style prompt
2. **Review originals** in `output/{name}/originals/`
3. **Pick your favorite** variant
4. **Use processed icons** from `output/{name}/processed/variant-{n}/`
5. **Drag into Xcode** Assets.xcassets

## Pro Tips

1. **Iterate on prompts** - Try different phrasings for better results
2. **Generate more variations** - Use `-v 8` to get more options
3. **Combine styles** - Mix multiple aesthetics for unique results
4. **Reference specific eras** - "1960s", "1920s", etc. work well
5. **Material descriptions** - "brushed metal", "frosted glass", "raw concrete"
6. **Use artist names** - "Donald Judd", "Mondrian", "Matisse" give strong visual cues

## Troubleshooting

**"REPLICATE_API_TOKEN not found"**
- Add your token to `.env` file
- Get it from: https://replicate.com/account/api-tokens

**Results don't match prompt**
- Increase `--guidance-scale` to 9.0 or 10.0
- Try more specific descriptors
- Reference specific artists or movements

**Generation failed**
- Check Replicate account has credits
- Try reducing `--steps` to 30
- Simplify your prompt

**Background not removed**
- Use `--remove-bg` explicitly
- Or manually remove using `--no-remove-bg` then edit

## Cost

- Approximately $0.01-0.05 per generation on Replicate
- Cost varies by model and number of steps
- 4 variations at 40 steps ≈ $0.03

## Integration

### Add to package.json

```json
{
  "scripts": {
    "icon": "python style_gen.py",
    "icon:interactive": "python style_gen.py -i",
    "icon:judd": "python style_gen.py judd"
  }
}
```

### Add alias to shell

```bash
# Add to ~/.zshrc or ~/.bashrc
alias icon-style='python /path/to/ios-app-icons/style_gen.py'
```

## Next Steps

- Check the main [README.md](README.md) for full documentation
- View [QUICKSTART.md](QUICKSTART.md) for basic setup
- Experiment with different artistic styles
- Share your favorite prompts!

## Credits

Built on top of:
- [Replicate](https://replicate.com/) - AI model hosting
- [Stable Diffusion](https://stability.ai/) - Image generation
- [rembg](https://github.com/danielgatis/rembg) - Background removal

---

**Happy icon creating! 🎨**
