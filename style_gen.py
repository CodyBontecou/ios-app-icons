#!/usr/bin/env python3
"""
Icon Style Generator - Interactive skill for custom style icon generation

Usage:
    python style_gen.py "your custom style prompt"
    python style_gen.py -i  # Interactive mode
"""

import sys
import subprocess
from pathlib import Path


PRESET_STYLES = {
    "judd": {
        "name": "Donald Judd",
        "prompt": "minimalist geometric stacked rectangles, aluminum and translucent plexiglass layers, Donald Judd sculpture, industrial materials, specific objects, clean precise forms",
        "subject": "image sharing icon"
    },
    "deco": {
        "name": "Art Deco",
        "prompt": "art deco geometric patterns, gold and black, 1920s style, elegant symmetry, luxury aesthetic",
        "subject": "app icon"
    },
    "pixel": {
        "name": "Pixel Art",
        "prompt": "pixel art retro gaming style, 8-bit colors, nostalgic, clean pixels, game icon",
        "subject": "app icon"
    },
    "watercolor": {
        "name": "Watercolor",
        "prompt": "watercolor painting, soft brushstrokes, pastel colors, artistic, flowing colors, hand-painted feel",
        "subject": "app icon"
    },
    "neon": {
        "name": "Neon",
        "prompt": "neon lights, glowing edges, cyberpunk aesthetic, vibrant colors, dark background, electric feel",
        "subject": "app icon"
    },
    "bauhaus": {
        "name": "Bauhaus",
        "prompt": "bauhaus design, geometric shapes, primary colors, modernist, functional beauty, circles squares triangles",
        "subject": "app icon"
    },
    "memphis": {
        "name": "Memphis Design",
        "prompt": "memphis design style, 1980s postmodern, geometric patterns, bright colors, playful shapes, squiggles and dots",
        "subject": "app icon"
    },
    "brutalism": {
        "name": "Brutalism",
        "prompt": "brutalist design, raw concrete texture, bold geometric forms, monolithic structure, stark minimalism",
        "subject": "app icon"
    }
}


def show_presets():
    """Display available preset styles."""
    print("\n🎨 Available Preset Styles:\n")
    for key, preset in PRESET_STYLES.items():
        print(f"  {key:12} - {preset['name']}")
    print()


def interactive_mode():
    """Run in interactive mode with preset selection."""
    print("\n🎨 Icon Style Generator - Interactive Mode\n")

    show_presets()

    choice = input("Choose a preset (or type 'custom' for custom prompt): ").strip().lower()

    if choice == "custom":
        custom_prompt = input("\nEnter your custom style prompt: ").strip()
        subject = input("Enter subject (default: 'app icon'): ").strip() or "app icon"
        prompt = custom_prompt
    elif choice in PRESET_STYLES:
        preset = PRESET_STYLES[choice]
        print(f"\n✨ Using {preset['name']} style")
        prompt = preset["prompt"]
        subject = preset["subject"]

        # Allow customization
        custom = input(f"\nSubject (default: '{subject}'): ").strip()
        if custom:
            subject = custom
    else:
        print(f"❌ Unknown preset: {choice}")
        sys.exit(1)

    variations = input("\nNumber of variations (default: 4): ").strip() or "4"

    print(f"\n🚀 Generating {variations} variations...")
    print(f"   Style: {prompt}")
    print(f"   Subject: {subject}\n")

    run_generator(subject, prompt, int(variations))


def run_generator(subject, custom_style, variations=4, steps=40, guidance=8.0):
    """Run the icon generator with custom style."""
    # Activate venv and run command
    venv_activate = Path("venv/bin/activate")

    cmd = [
        "icon-gen", "generate",
        "--subject", subject,
        "--style", "custom",
        "--custom-style", custom_style,
        "--variations", str(variations),
        "--steps", str(steps),
        "--guidance-scale", str(guidance)
    ]

    # Run with activated venv
    if venv_activate.exists():
        shell_cmd = f"source {venv_activate} && {' '.join(cmd)}"
        subprocess.run(shell_cmd, shell=True, check=True)
    else:
        subprocess.run(cmd, check=True)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("\n🎨 Icon Style Generator\n")
        print("Usage:")
        print("  python style_gen.py \"your custom style prompt\"")
        print("  python style_gen.py -i                          # Interactive mode")
        print("  python style_gen.py --presets                   # Show preset styles")
        print("\nExamples:")
        print("  python style_gen.py judd")
        print("  python style_gen.py \"minimalist geometric art\"")
        print()
        sys.exit(1)

    arg = sys.argv[1]

    if arg in ["-i", "--interactive"]:
        interactive_mode()
    elif arg in ["--presets", "-p"]:
        show_presets()
    elif arg in PRESET_STYLES:
        # Use preset
        preset = PRESET_STYLES[arg]
        print(f"\n✨ Using {preset['name']} style")
        run_generator(preset["subject"], preset["prompt"])
    else:
        # Custom prompt
        custom_style = arg
        subject = sys.argv[2] if len(sys.argv) > 2 else "app icon"
        run_generator(subject, custom_style)


if __name__ == "__main__":
    main()
