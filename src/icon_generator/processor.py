"""Image post-processing for iOS app icons."""

from pathlib import Path
from typing import List, Optional, Dict
from PIL import Image, ImageDraw
from rembg import remove
from .config import Config


class IconProcessor:
    """Handles image post-processing and multi-size generation."""

    @staticmethod
    def remove_background(image_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Remove background from an image using rembg.

        Args:
            image_path: Path to input image
            output_path: Path to save processed image (optional)

        Returns:
            Path to the processed image
        """
        if output_path is None:
            output_path = image_path.parent / f"{image_path.stem}_nobg.png"

        with open(image_path, 'rb') as input_file:
            input_data = input_file.read()
            output_data = remove(input_data)

        with open(output_path, 'wb') as output_file:
            output_file.write(output_data)

        return output_path

    @staticmethod
    def apply_ios_mask(image: Image.Image, size: int) -> Image.Image:
        """
        Apply iOS-style rounded corner mask to an image.

        iOS uses a continuous corner radius that varies by icon size.
        Approximation: radius ≈ size * 0.2237 (22.37% of size)

        Args:
            image: PIL Image to mask
            size: Target size (width/height)

        Returns:
            Masked PIL Image with transparency
        """
        # Resize image to target size
        image = image.resize((size, size), Image.Resampling.LANCZOS)

        # Calculate corner radius (iOS standard)
        radius = int(size * 0.2237)

        # Create a mask with rounded corners
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), (size, size)], radius=radius, fill=255)

        # Apply mask to image
        output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        output.paste(image, (0, 0))
        output.putalpha(mask)

        return output

    @staticmethod
    def generate_all_sizes(
        input_path: Path,
        output_dir: Path,
        sizes: Optional[List[int]] = None,
        apply_mask: bool = True,
        remove_bg: bool = False
    ) -> List[Path]:
        """
        Generate all iOS app icon sizes from a source image.

        Args:
            input_path: Path to source image
            output_dir: Directory to save resized icons
            sizes: List of sizes to generate (defaults to Config.IOS_ICON_SIZES)
            apply_mask: Whether to apply iOS rounded corner mask
            remove_bg: Whether to remove background first

        Returns:
            List of paths to generated icon files
        """
        if sizes is None:
            sizes = Config.IOS_ICON_SIZES

        output_dir.mkdir(parents=True, exist_ok=True)

        # Load the source image
        image = Image.open(input_path)

        # Remove background if requested
        if remove_bg:
            print("🔄 Removing background...")
            temp_path = output_dir / "temp_nobg.png"
            temp_path = IconProcessor.remove_background(input_path, temp_path)
            image = Image.open(temp_path)
            temp_path.unlink()  # Clean up temp file

        # Ensure RGBA mode
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        generated_paths = []

        for size in sorted(sizes, reverse=True):
            print(f"📐 Generating {size}x{size}...")

            if apply_mask:
                resized = IconProcessor.apply_ios_mask(image, size)
            else:
                resized = image.resize((size, size), Image.Resampling.LANCZOS)

            # Save with optimized PNG compression
            output_path = output_dir / f"AppIcon-{size}.png"
            resized.save(output_path, 'PNG', optimize=True)
            generated_paths.append(output_path)

        return generated_paths

    @staticmethod
    def process_generated_icons(
        originals_dir: Path,
        output_base_dir: Path,
        remove_bg: bool = True,
        apply_mask: bool = True
    ) -> Dict[str, List[Path]]:
        """
        Process all generated icons from the originals directory.

        Args:
            originals_dir: Directory containing original generated images
            output_base_dir: Base output directory
            remove_bg: Whether to remove backgrounds
            apply_mask: Whether to apply iOS masks

        Returns:
            Dictionary mapping variant names to lists of generated paths
        """
        processed_dir = output_base_dir / "processed"
        processed_dir.mkdir(parents=True, exist_ok=True)

        results = {}

        # Process each variant
        original_images = sorted(originals_dir.glob("variant-*.png"))

        for idx, original_path in enumerate(original_images, 1):
            variant_name = original_path.stem
            print(f"\n🎨 Processing {variant_name}...")

            # Create variant subdirectory
            variant_dir = processed_dir / variant_name
            variant_dir.mkdir(exist_ok=True)

            # Generate all sizes
            paths = IconProcessor.generate_all_sizes(
                input_path=original_path,
                output_dir=variant_dir,
                remove_bg=remove_bg,
                apply_mask=apply_mask
            )

            results[variant_name] = paths
            print(f"✅ Processed {len(paths)} sizes for {variant_name}")

        return results
