"""Command-line interface for the iOS App Icon Generator."""

import click
from pathlib import Path
from .config import Config
from .generator import IconGenerator
from .processor import IconProcessor


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """iOS App Icon Generator - AI-powered app icon creation."""
    pass


@cli.command()
@click.option(
    '--subject',
    required=True,
    help='What to generate (e.g., "happy cat", "mountain logo")'
)
@click.option(
    '--style',
    type=click.Choice(['ios', 'flat', 'vector', 'custom']),
    default='ios',
    help='Icon style to generate'
)
@click.option(
    '--custom-style',
    type=str,
    default=None,
    help='Full custom prompt (required when style="custom")'
)
@click.option(
    '--variations',
    type=int,
    default=4,
    help='Number of variations to generate'
)
@click.option(
    '--color',
    type=str,
    default=None,
    help='Background color (for flat style)'
)
@click.option(
    '--no-process',
    is_flag=True,
    help='Skip post-processing (only generate original images)'
)
@click.option(
    '--no-mask',
    is_flag=True,
    help='Skip iOS rounded corner mask'
)
@click.option(
    '--no-remove-bg',
    is_flag=True,
    help='Skip background removal'
)
@click.option(
    '--output-dir',
    type=click.Path(),
    default=None,
    help='Custom output directory'
)
@click.option(
    '--model',
    type=click.Choice(['sdxl', 'flux-schnell', 'flux-dev', 'flux-pro']),
    default='sdxl',
    help='AI model to use for generation'
)
@click.option(
    '--steps',
    type=int,
    default=None,
    help='Number of inference steps (uses model default if not set)'
)
@click.option(
    '--guidance-scale',
    type=float,
    default=None,
    help='Guidance scale (uses model default if not set)'
)
def generate(
    subject: str,
    style: str,
    custom_style: str,
    variations: int,
    color: str,
    no_process: bool,
    no_mask: bool,
    no_remove_bg: bool,
    output_dir: str,
    model: str,
    steps: int,
    guidance_scale: float
):
    """Generate AI-powered app icons."""

    try:
        # Validate custom style requirement
        if style == "custom" and not custom_style:
            click.echo("❌ Error: --custom-style is required when using --style=custom", err=True)
            raise click.Abort()

        # Validate configuration
        Config.validate()

        # Set up output directory
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = Config.get_output_dir(subject)

        click.echo(f"\n🚀 iOS App Icon Generator")
        click.echo(f"📁 Output directory: {output_path}\n")

        # Initialize generator
        generator = IconGenerator()

        # Build generation params (only include if set)
        gen_params = {}
        if steps is not None:
            gen_params["steps"] = steps
        if guidance_scale is not None:
            gen_params["guidance_scale"] = guidance_scale

        # Generate icons
        generated_paths = generator.generate(
            subject=subject,
            style=style,
            variations=variations,
            color=color,
            custom_style=custom_style,
            output_dir=output_path,
            model=model,
            **gen_params
        )

        click.echo(f"\n✨ Generated {len(generated_paths)} variations!")

        # Post-process if not disabled
        if not no_process:
            click.echo(f"\n🔧 Post-processing icons...")

            originals_dir = output_path / "originals"
            results = IconProcessor.process_generated_icons(
                originals_dir=originals_dir,
                output_base_dir=output_path,
                remove_bg=not no_remove_bg,
                apply_mask=not no_mask
            )

            total_processed = sum(len(paths) for paths in results.values())
            click.echo(f"\n✅ Generated {total_processed} processed icons!")

            # Show summary
            click.echo(f"\n📊 Summary:")
            click.echo(f"   Original images: {len(generated_paths)}")
            click.echo(f"   Processed variants: {len(results)}")
            click.echo(f"   Total icon sizes: {total_processed}")
            click.echo(f"   Output location: {output_path}")
        else:
            click.echo(f"\n⏭️  Skipped post-processing (--no-process flag)")
            click.echo(f"   Original images: {len(generated_paths)}")
            click.echo(f"   Location: {output_path / 'originals'}")

        click.echo(f"\n🎉 Done! Your icons are ready at: {output_path}")

    except ValueError as e:
        click.echo(f"\n❌ Configuration Error: {e}", err=True)
        click.echo(f"\n💡 Tip: Copy .env.example to .env and add your Replicate API token")
        raise click.Abort()

    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        raise


@cli.command()
@click.option(
    '--subject',
    required=True,
    help='What to generate (e.g., "product showcase", "sunset beach")'
)
@click.option(
    '--style',
    type=click.Choice(['ios', 'flat', 'vector', 'custom']),
    default='custom',
    help='Visual style to use'
)
@click.option(
    '--custom-style',
    type=str,
    default=None,
    help='Full custom prompt (required when style="custom")'
)
@click.option(
    '--aspect-ratio',
    type=click.Choice(['square', 'portrait', 'landscape', 'story']),
    default='square',
    help='Instagram aspect ratio (square=1:1, portrait=4:5, landscape=1.91:1, story=9:16)'
)
@click.option(
    '--variations',
    type=int,
    default=4,
    help='Number of variations to generate'
)
@click.option(
    '--no-process',
    is_flag=True,
    help='Skip post-processing (only generate original images)'
)
@click.option(
    '--output-dir',
    type=click.Path(),
    default=None,
    help='Custom output directory'
)
@click.option(
    '--model',
    type=click.Choice(['sdxl', 'flux-schnell', 'flux-dev', 'flux-pro']),
    default='sdxl',
    help='AI model (flux models have better text rendering)'
)
@click.option(
    '--steps',
    type=int,
    default=None,
    help='Number of inference steps (uses model default if not set)'
)
@click.option(
    '--guidance-scale',
    type=float,
    default=None,
    help='Guidance scale (uses model default if not set)'
)
@click.option(
    '--text',
    type=str,
    default=None,
    help='Text to overlay on the image (post-processing)'
)
@click.option(
    '--text-position',
    type=click.Choice(['top', 'center', 'bottom']),
    default='top',
    help='Position of text overlay'
)
@click.option(
    '--text-color',
    type=str,
    default='black',
    help='Text color (black, white, or hex like #FF0000)'
)
@click.option(
    '--no-text-box',
    is_flag=True,
    help='Remove background box behind text'
)
@click.option(
    '--text-style',
    type=click.Choice(['classic', 'brutalist']),
    default='classic',
    help='Text style: classic (serif) or brutalist (monospace, bold, wide tracking)'
)
@click.option(
    '--layout',
    type=click.Choice(['overlay', 'card']),
    default='overlay',
    help='Layout style: overlay (text on image) or card (image top, text below on solid bg)'
)
@click.option(
    '--bg-color',
    type=str,
    default='black',
    help='Background color for card layout (black, white, or hex like #1a1a1a)'
)
def instagram(
    subject: str,
    style: str,
    custom_style: str,
    aspect_ratio: str,
    variations: int,
    no_process: bool,
    output_dir: str,
    model: str,
    steps: int,
    guidance_scale: float,
    text: str,
    text_position: str,
    text_color: str,
    no_text_box: bool,
    text_style: str,
    layout: str,
    bg_color: str
):
    """Generate AI-powered Instagram posts."""

    try:
        # Validate custom style requirement
        if style == "custom" and not custom_style:
            click.echo("❌ Error: --custom-style is required when using --style=custom", err=True)
            raise click.Abort()

        # Validate configuration
        Config.validate()

        # Set up output directory
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = Config.get_output_dir(subject)

        # Get dimensions for display
        width, height = Config.INSTAGRAM_SIZES.get(aspect_ratio, (1080, 1080))

        click.echo(f"\n📸 Instagram Post Generator")
        click.echo(f"📐 Aspect ratio: {aspect_ratio} ({width}x{height})")
        click.echo(f"📁 Output directory: {output_path}\n")

        # Initialize generator
        generator = IconGenerator()

        # Build generation params (only include if set)
        gen_params = {}
        if steps is not None:
            gen_params["steps"] = steps
        if guidance_scale is not None:
            gen_params["guidance_scale"] = guidance_scale

        # Generate images
        generated_paths = generator.generate(
            subject=subject,
            style=style,
            variations=variations,
            custom_style=custom_style,
            output_dir=output_path,
            model=model,
            format="instagram",
            aspect_ratio=aspect_ratio,
            **gen_params
        )

        click.echo(f"\n✨ Generated {len(generated_paths)} variations!")

        # Post-process if not disabled
        if not no_process:
            click.echo(f"\n🔧 Processing for Instagram...")

            originals_dir = output_path / "originals"

            # Parse text color
            if text_color.lower() == 'black':
                parsed_text_color = (0, 0, 0)
            elif text_color.lower() == 'white':
                parsed_text_color = (255, 255, 255)
            elif text_color.startswith('#'):
                hex_color = text_color.lstrip('#')
                parsed_text_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            else:
                parsed_text_color = (0, 0, 0)

            # Determine box color based on text color
            if no_text_box:
                box_color = None
            elif parsed_text_color == (255, 255, 255):
                box_color = None  # White text usually means no box
            else:
                box_color = (255, 255, 255)  # White box for dark text

            # Parse background color for card layout
            if bg_color.lower() == 'black':
                parsed_bg_color = (0, 0, 0)
            elif bg_color.lower() == 'white':
                parsed_bg_color = (255, 255, 255)
            elif bg_color.startswith('#'):
                hex_bg = bg_color.lstrip('#')
                parsed_bg_color = tuple(int(hex_bg[i:i+2], 16) for i in (0, 2, 4))
            else:
                parsed_bg_color = (0, 0, 0)

            if text and layout == 'card':
                # Card layout: image on top, text below on solid background
                results = IconProcessor.process_card_layout(
                    originals_dir=originals_dir,
                    output_base_dir=output_path,
                    text=text,
                    aspect_ratio=aspect_ratio,
                    bg_color=parsed_bg_color,
                    text_color=parsed_text_color
                )
            elif text:
                results = IconProcessor.process_instagram_with_text(
                    originals_dir=originals_dir,
                    output_base_dir=output_path,
                    text=text,
                    aspect_ratio=aspect_ratio,
                    position=text_position,
                    text_color=parsed_text_color,
                    box_color=box_color,
                    text_style=text_style
                )
            else:
                results = IconProcessor.process_instagram_images(
                    originals_dir=originals_dir,
                    output_base_dir=output_path,
                    aspect_ratio=aspect_ratio
                )

            total_processed = sum(len(paths) for paths in results.values())
            click.echo(f"\n✅ Generated {total_processed} Instagram posts!")

            # Show summary
            click.echo(f"\n📊 Summary:")
            click.echo(f"   Original images: {len(generated_paths)}")
            click.echo(f"   Instagram posts: {total_processed}")
            click.echo(f"   Dimensions: {width}x{height}")
            if text:
                click.echo(f"   Text overlay: \"{text[:50]}{'...' if len(text) > 50 else ''}\"")
            click.echo(f"   Output location: {output_path}")
        else:
            click.echo(f"\n⏭️  Skipped post-processing (--no-process flag)")
            click.echo(f"   Original images: {len(generated_paths)}")
            click.echo(f"   Location: {output_path / 'originals'}")

        click.echo(f"\n🎉 Done! Your Instagram posts are ready at: {output_path}")

    except ValueError as e:
        click.echo(f"\n❌ Configuration Error: {e}", err=True)
        click.echo(f"\n💡 Tip: Copy .env.example to .env and add your Replicate API token")
        raise click.Abort()

    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        raise


@cli.command()
def info():
    """Show configuration and system information."""
    click.echo("\n📋 iOS App Icon Generator - Configuration\n")

    # Check API token
    has_token = bool(Config.REPLICATE_API_TOKEN)
    token_status = "✅ Set" if has_token else "❌ Not set"
    click.echo(f"API Token: {token_status}")

    if not has_token:
        click.echo("   Get your token from: https://replicate.com/account/api-tokens")

    # Show configuration
    click.echo(f"\nDefault Settings:")
    click.echo(f"   Output directory: {Config.OUTPUT_DIR}")
    click.echo(f"   Image size: {Config.DEFAULT_SIZE}x{Config.DEFAULT_SIZE}")
    click.echo(f"   Inference steps: {Config.DEFAULT_STEPS}")
    click.echo(f"   Guidance scale: {Config.DEFAULT_GUIDANCE_SCALE}")
    click.echo(f"   Default variations: {Config.DEFAULT_VARIATIONS}")

    click.echo(f"\nSupported Styles:")
    click.echo(f"   • ios    - iOS-style rounded app icons")
    click.echo(f"   • flat   - Minimalist flat design icons")
    click.echo(f"   • vector - Vector illustration style")
    click.echo(f"   • custom - Custom prompt (use --custom-style)")

    click.echo(f"\nAvailable Models:")
    for name, config in Config.MODELS.items():
        default = " (default)" if name == Config.DEFAULT_MODEL else ""
        click.echo(f"   • {name}{default} - {config['description']}")

    click.echo(f"\niOS Icon Sizes:")
    sizes_str = ", ".join(str(s) for s in Config.IOS_ICON_SIZES)
    click.echo(f"   {sizes_str}")

    click.echo(f"\nInstagram Sizes:")
    for name, (w, h) in Config.INSTAGRAM_SIZES.items():
        click.echo(f"   • {name}: {w}x{h}")

    click.echo()


if __name__ == '__main__':
    cli()
