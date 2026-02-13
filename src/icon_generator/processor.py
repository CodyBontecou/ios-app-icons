"""Image post-processing for iOS app icons."""

from pathlib import Path
from typing import List, Optional, Dict, Tuple
from PIL import Image, ImageDraw, ImageFont
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

    @staticmethod
    def generate_instagram_sizes(
        input_path: Path,
        output_dir: Path,
        aspect_ratio: str = "square"
    ) -> List[Path]:
        """
        Generate Instagram-optimized images (no masking, proper dimensions).

        Args:
            input_path: Path to source image
            output_dir: Directory to save resized images
            aspect_ratio: Instagram aspect ratio (square, portrait, landscape, story)

        Returns:
            List of paths to generated image files
        """
        from PIL import ImageFilter

        output_dir.mkdir(parents=True, exist_ok=True)

        # Get target dimensions
        target_size = Config.INSTAGRAM_SIZES.get(aspect_ratio, (1080, 1080))
        target_width, target_height = target_size

        # Load the source image
        image = Image.open(input_path)

        # Ensure RGB mode for Instagram (no transparency needed)
        if image.mode == 'RGBA':
            # Create white background for transparency
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')

        # Resize to target dimensions
        resized = image.resize((target_width, target_height), Image.Resampling.LANCZOS)

        # Apply slight sharpening for social media clarity
        sharpened = resized.filter(ImageFilter.UnsharpMask(radius=1, percent=50, threshold=3))

        # Save with high quality
        output_path = output_dir / f"post-{target_width}x{target_height}.png"
        sharpened.save(output_path, 'PNG', optimize=True)

        return [output_path]

    @staticmethod
    def process_instagram_images(
        originals_dir: Path,
        output_base_dir: Path,
        aspect_ratio: str = "square"
    ) -> Dict[str, List[Path]]:
        """
        Process all generated images for Instagram output.

        Args:
            originals_dir: Directory containing original generated images
            output_base_dir: Base output directory
            aspect_ratio: Instagram aspect ratio

        Returns:
            Dictionary mapping variant names to lists of generated paths
        """
        instagram_dir = output_base_dir / "instagram"
        instagram_dir.mkdir(parents=True, exist_ok=True)

        results = {}

        # Process each variant
        original_images = sorted(originals_dir.glob("variant-*.png"))

        for idx, original_path in enumerate(original_images, 1):
            variant_name = original_path.stem
            print(f"\n📸 Processing {variant_name} for Instagram...")

            # Create variant subdirectory
            variant_dir = instagram_dir / variant_name
            variant_dir.mkdir(exist_ok=True)

            # Generate Instagram size
            paths = IconProcessor.generate_instagram_sizes(
                input_path=original_path,
                output_dir=variant_dir,
                aspect_ratio=aspect_ratio
            )

            results[variant_name] = paths
            print(f"✅ Processed Instagram image for {variant_name}")

        return results

    @staticmethod
    def add_text_overlay(
        image: Image.Image,
        text: str,
        position: str = "top",
        text_color: Tuple[int, int, int] = (0, 0, 0),
        box_color: Optional[Tuple[int, int, int]] = (255, 255, 255),
        font_size: Optional[int] = None,
        padding: int = 40,
        margin: int = 60,
        style: str = "classic"
    ) -> Image.Image:
        """
        Add text overlay to an image.

        Args:
            image: PIL Image to add text to
            text: Text to overlay
            position: "top", "center", or "bottom"
            text_color: RGB tuple for text color
            box_color: RGB tuple for background box (None for no box)
            font_size: Font size (auto-calculated if None)
            padding: Padding inside text box
            margin: Margin from edge of image
            style: "classic" (serif) or "brutalist" (monospace, bold, wide tracking)

        Returns:
            Image with text overlay
        """
        image = image.copy()
        draw = ImageDraw.Draw(image)
        width, height = image.size

        # Style-specific settings
        if style == "brutalist":
            # Brutalist: large monospace, bold, wide letter-spacing
            if font_size is None:
                font_size = int(width * 0.055)  # Large but fits
            letter_spacing = 0.12  # Wide tracking
            text = text.upper()  # Brutalist often uses uppercase

            # Try to load monospace fonts (JetBrains Mono, SF Mono, etc.)
            font = None
            mono_fonts = [
                "/System/Library/Fonts/SFMono-Bold.otf",
                "/System/Library/Fonts/Supplemental/JetBrains Mono Bold.ttf",
                "/Library/Fonts/JetBrainsMono-Bold.ttf",
                "/System/Library/Fonts/Monaco.ttf",
                "/System/Library/Fonts/Menlo.ttc",
                "/System/Library/Fonts/Supplemental/Courier New Bold.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            ]
            for font_path in mono_fonts:
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    break
                except (OSError, IOError):
                    continue
        else:
            # Classic: serif font
            if font_size is None:
                font_size = int(width * 0.045)
            letter_spacing = 0

            font = None
            serif_fonts = [
                "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
                "/System/Library/Fonts/Times.ttc",
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
                "/usr/share/fonts/TTF/times.ttf",
            ]
            for font_path in serif_fonts:
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    break
                except (OSError, IOError):
                    continue

        if font is None:
            font = ImageFont.load_default()

        # Calculate text dimensions with word wrapping
        # Use larger margins for brutalist style to ensure text fits
        effective_margin = margin * 1.5 if style == "brutalist" else margin
        max_text_width = width - (int(effective_margin) * 2) - (padding * 2)
        lines = IconProcessor._wrap_text(text, font, max_text_width, draw, letter_spacing)

        # Calculate total text block height
        line_height = font_size * 1.4
        total_text_height = len(lines) * line_height

        # Calculate box dimensions
        box_width = max_text_width + (padding * 2)
        box_height = total_text_height + (padding * 2)

        # Calculate position
        box_x = (width - box_width) // 2
        if position == "top":
            box_y = int(effective_margin) + int(height * 0.1)
        elif position == "bottom":
            box_y = height - box_height - int(effective_margin) - int(height * 0.08)
        else:  # center
            box_y = (height - box_height) // 2

        # Draw background box if specified
        if box_color is not None:
            draw.rectangle(
                [(box_x, box_y), (box_x + box_width, box_y + box_height)],
                fill=box_color
            )

        # Draw text lines
        text_y = box_y + padding

        # For brutalist style without box, add shadow for readability
        add_shadow = (style == "brutalist" and box_color is None)
        shadow_color = (0, 0, 0)  # Black shadow
        shadow_offset = max(2, int(font_size * 0.04))

        for line in lines:
            if letter_spacing > 0:
                # Draw with letter spacing
                line_width = IconProcessor._get_text_width_with_spacing(line, font, letter_spacing, draw)
                line_x = box_x + (box_width - line_width) // 2
                # Draw shadow first if needed
                if add_shadow:
                    IconProcessor._draw_text_with_spacing(draw, line_x + shadow_offset, text_y + shadow_offset, line, font, shadow_color, letter_spacing)
                IconProcessor._draw_text_with_spacing(draw, line_x, text_y, line, font, text_color, letter_spacing)
            else:
                # Normal text drawing
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                line_x = box_x + (box_width - line_width) // 2
                # Draw shadow first if needed
                if add_shadow:
                    draw.text((line_x + shadow_offset, text_y + shadow_offset), line, fill=shadow_color, font=font)
                draw.text((line_x, text_y), line, fill=text_color, font=font)
            text_y += line_height

        return image

    @staticmethod
    def _get_text_width_with_spacing(text: str, font: ImageFont.ImageFont, spacing: float, draw: ImageDraw.ImageDraw) -> int:
        """Calculate text width with letter spacing."""
        total_width = 0
        for i, char in enumerate(text):
            bbox = draw.textbbox((0, 0), char, font=font)
            char_width = bbox[2] - bbox[0]
            total_width += char_width
            if i < len(text) - 1:
                # Add spacing based on font size
                total_width += int(font.size * spacing)
        return total_width

    @staticmethod
    def _draw_text_with_spacing(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, font: ImageFont.ImageFont, color: Tuple[int, int, int], spacing: float):
        """Draw text with letter spacing."""
        current_x = x
        for i, char in enumerate(text):
            draw.text((current_x, y), char, fill=color, font=font)
            bbox = draw.textbbox((0, 0), char, font=font)
            char_width = bbox[2] - bbox[0]
            current_x += char_width
            if i < len(text) - 1:
                current_x += int(font.size * spacing)

    @staticmethod
    def _wrap_text(text: str, font: ImageFont.ImageFont, max_width: int, draw: ImageDraw.ImageDraw, letter_spacing: float = 0) -> List[str]:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            if letter_spacing > 0:
                line_width = IconProcessor._get_text_width_with_spacing(test_line, font, letter_spacing, draw)
            else:
                bbox = draw.textbbox((0, 0), test_line, font=font)
                line_width = bbox[2] - bbox[0]

            if line_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    @staticmethod
    def generate_card_layout(
        input_path: Path,
        output_dir: Path,
        text: str,
        aspect_ratio: str = "square",
        bg_color: Tuple[int, int, int] = (0, 0, 0),
        text_color: Tuple[int, int, int] = (255, 255, 255),
        image_ratio: float = 0.6
    ) -> List[Path]:
        """
        Generate card layout with image on top, text below on solid background.
        Similar to Daniela Koe's style posts.

        Args:
            input_path: Path to source image
            output_dir: Directory to save output
            text: Text to display below image
            aspect_ratio: Instagram aspect ratio
            bg_color: Background color (default black)
            text_color: Text color (default white)
            image_ratio: Portion of height for image (0.0-1.0, default 0.6)

        Returns:
            List of output paths
        """
        from PIL import ImageFilter, ImageOps

        output_dir.mkdir(parents=True, exist_ok=True)

        # Get target dimensions
        target_size = Config.INSTAGRAM_SIZES.get(aspect_ratio, (1080, 1080))
        target_width, target_height = target_size

        # Create canvas with background color
        canvas = Image.new('RGB', (target_width, target_height), bg_color)

        # Load image
        image = Image.open(input_path)
        if image.mode == 'RGBA':
            # Use bg_color for transparency
            background = Image.new('RGB', image.size, bg_color)
            background.paste(image, mask=image.split()[3])
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')

        # Calculate image area dimensions
        image_area_height = int(target_height * image_ratio)

        # Resize image to fit width, maintaining aspect ratio
        img_aspect = image.width / image.height
        target_img_width = target_width
        target_img_height = int(target_width / img_aspect)

        # If image is too tall, fit to height instead
        if target_img_height > image_area_height:
            target_img_height = image_area_height
            target_img_width = int(image_area_height * img_aspect)

        resized_img = image.resize((target_img_width, target_img_height), Image.Resampling.LANCZOS)

        # Center image horizontally, position at top
        img_x = (target_width - target_img_width) // 2
        img_y = (image_area_height - target_img_height) // 2

        canvas.paste(resized_img, (img_x, img_y))

        # Add text below image
        draw = ImageDraw.Draw(canvas)

        # Load serif font
        font_size = int(target_width * 0.042)  # Clean readable size
        font = None
        serif_fonts = [
            "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
            "/System/Library/Fonts/Times.ttc",
            "/Library/Fonts/Georgia.ttf",
            "/System/Library/Fonts/Supplemental/Georgia.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        ]
        for font_path in serif_fonts:
            try:
                font = ImageFont.truetype(font_path, font_size)
                break
            except (OSError, IOError):
                continue
        if font is None:
            font = ImageFont.load_default()

        # Text area
        text_margin = int(target_width * 0.08)
        text_top = image_area_height + int(target_height * 0.05)
        max_text_width = target_width - (text_margin * 2)

        # Wrap text
        lines = IconProcessor._wrap_text(text, font, max_text_width, draw)

        # Draw text lines (left-aligned)
        line_height = font_size * 1.5
        y = text_top
        for line in lines:
            draw.text((text_margin, y), line, fill=text_color, font=font)
            y += line_height

        # Save
        output_path = output_dir / f"post-{target_width}x{target_height}.png"
        canvas.save(output_path, 'PNG', optimize=True)

        return [output_path]

    @staticmethod
    def process_card_layout(
        originals_dir: Path,
        output_base_dir: Path,
        text: str,
        aspect_ratio: str = "square",
        bg_color: Tuple[int, int, int] = (0, 0, 0),
        text_color: Tuple[int, int, int] = (255, 255, 255),
        image_ratio: float = 0.6
    ) -> Dict[str, List[Path]]:
        """
        Process all images with card layout (image top, text bottom).

        Args:
            originals_dir: Directory containing original generated images
            output_base_dir: Base output directory
            text: Text to display below image
            aspect_ratio: Instagram aspect ratio
            bg_color: Background color
            text_color: Text color
            image_ratio: Portion of height for image

        Returns:
            Dictionary mapping variant names to lists of generated paths
        """
        instagram_dir = output_base_dir / "instagram"
        instagram_dir.mkdir(parents=True, exist_ok=True)

        results = {}
        original_images = sorted(originals_dir.glob("variant-*.png"))

        for idx, original_path in enumerate(original_images, 1):
            variant_name = original_path.stem
            print(f"\n📸 Processing {variant_name} with card layout...")

            variant_dir = instagram_dir / variant_name
            variant_dir.mkdir(exist_ok=True)

            paths = IconProcessor.generate_card_layout(
                input_path=original_path,
                output_dir=variant_dir,
                text=text,
                aspect_ratio=aspect_ratio,
                bg_color=bg_color,
                text_color=text_color,
                image_ratio=image_ratio
            )

            results[variant_name] = paths
            print(f"✅ Processed card layout for {variant_name}")

        return results

    @staticmethod
    def generate_instagram_with_text(
        input_path: Path,
        output_dir: Path,
        text: str,
        aspect_ratio: str = "square",
        position: str = "top",
        text_color: Tuple[int, int, int] = (0, 0, 0),
        box_color: Optional[Tuple[int, int, int]] = (255, 255, 255),
        text_style: str = "classic"
    ) -> List[Path]:
        """
        Generate Instagram image with text overlay.

        Args:
            input_path: Path to source image
            output_dir: Directory to save output
            text: Text to overlay on image
            aspect_ratio: Instagram aspect ratio
            position: Text position ("top", "center", "bottom")
            text_color: RGB color for text
            box_color: RGB color for text box background (None for no box)
            text_style: "classic" (serif) or "brutalist" (monospace, bold)

        Returns:
            List of output paths
        """
        from PIL import ImageFilter

        output_dir.mkdir(parents=True, exist_ok=True)

        # Get target dimensions
        target_size = Config.INSTAGRAM_SIZES.get(aspect_ratio, (1080, 1080))
        target_width, target_height = target_size

        # Load and resize image
        image = Image.open(input_path)

        if image.mode == 'RGBA':
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')

        resized = image.resize((target_width, target_height), Image.Resampling.LANCZOS)

        # Add text overlay
        with_text = IconProcessor.add_text_overlay(
            resized,
            text,
            position=position,
            text_color=text_color,
            box_color=box_color,
            style=text_style
        )

        # Apply slight sharpening
        sharpened = with_text.filter(ImageFilter.UnsharpMask(radius=1, percent=50, threshold=3))

        # Save
        output_path = output_dir / f"post-{target_width}x{target_height}.png"
        sharpened.save(output_path, 'PNG', optimize=True)

        return [output_path]

    @staticmethod
    def process_instagram_with_text(
        originals_dir: Path,
        output_base_dir: Path,
        text: str,
        aspect_ratio: str = "square",
        position: str = "top",
        text_color: Tuple[int, int, int] = (0, 0, 0),
        box_color: Optional[Tuple[int, int, int]] = (255, 255, 255),
        text_style: str = "classic"
    ) -> Dict[str, List[Path]]:
        """
        Process all generated images for Instagram with text overlay.

        Args:
            originals_dir: Directory containing original generated images
            output_base_dir: Base output directory
            text: Text to overlay
            aspect_ratio: Instagram aspect ratio
            position: Text position
            text_color: Text color
            box_color: Box background color (None for no box)
            text_style: "classic" (serif) or "brutalist" (monospace, bold)

        Returns:
            Dictionary mapping variant names to lists of generated paths
        """
        instagram_dir = output_base_dir / "instagram"
        instagram_dir.mkdir(parents=True, exist_ok=True)

        results = {}
        original_images = sorted(originals_dir.glob("variant-*.png"))

        for idx, original_path in enumerate(original_images, 1):
            variant_name = original_path.stem
            print(f"\n📸 Processing {variant_name} with text overlay...")

            variant_dir = instagram_dir / variant_name
            variant_dir.mkdir(exist_ok=True)

            paths = IconProcessor.generate_instagram_with_text(
                input_path=original_path,
                output_dir=variant_dir,
                text=text,
                aspect_ratio=aspect_ratio,
                position=position,
                text_color=text_color,
                box_color=box_color,
                text_style=text_style
            )

            results[variant_name] = paths
            print(f"✅ Processed Instagram image with text for {variant_name}")

        return results
