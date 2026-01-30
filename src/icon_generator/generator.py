"""Core generation logic using Replicate API."""

import time
from pathlib import Path
from typing import List, Dict, Optional
import replicate
import requests
from .config import Config
from .prompts import IconPrompts


class IconGenerator:
    """Handles AI-powered icon generation using Replicate."""

    def __init__(self, api_token: Optional[str] = None):
        """Initialize the generator with API credentials."""
        self.api_token = api_token or Config.REPLICATE_API_TOKEN
        if not self.api_token:
            raise ValueError(
                "Replicate API token is required. "
                "Set REPLICATE_API_TOKEN in your .env file or pass it directly."
            )

    def generate(
        self,
        subject: str,
        style: str = "ios",
        variations: int = 4,
        color: Optional[str] = None,
        custom_style: Optional[str] = None,
        output_dir: Optional[Path] = None,
        model: Optional[str] = None,
        format: str = "ios",
        aspect_ratio: str = "square",
        **generation_params
    ) -> List[Path]:
        """
        Generate app icon or Instagram post variations.

        Args:
            subject: What to generate (e.g., "happy cat", "mountain logo")
            style: Icon style (ios, flat, vector, custom)
            variations: Number of variations to generate
            color: Background color (for flat style)
            custom_style: Full custom prompt for style="custom"
            output_dir: Directory to save generated images
            model: Replicate model to use (defaults to Config.DEFAULT_MODEL)
            format: Output format ("ios" for app icons, "instagram" for social media)
            aspect_ratio: For Instagram: "square", "portrait", "landscape", "story"
            **generation_params: Additional parameters for the model

        Returns:
            List of paths to generated images
        """
        # Enhance subject and build prompt
        enhanced_subject = IconPrompts.enhance_subject(subject)
        prompt_data = IconPrompts.build_prompt(
            enhanced_subject,
            style=style,
            color=color,
            custom_style=custom_style,
            format=format
        )

        # Set up output directory
        if output_dir is None:
            output_dir = Config.get_output_dir(subject)
        originals_dir = output_dir / "originals"
        originals_dir.mkdir(parents=True, exist_ok=True)

        # Determine dimensions based on format
        if format == "instagram":
            width, height = Config.INSTAGRAM_SIZES.get(aspect_ratio, (1080, 1080))
        else:
            width = Config.DEFAULT_SIZE
            height = Config.DEFAULT_SIZE

        # Prepare generation parameters
        model_name = model or Config.DEFAULT_MODEL
        params = {
            "prompt": prompt_data["prompt"],
            "negative_prompt": prompt_data["negative_prompt"],
            "num_outputs": variations,
            "width": width,
            "height": height,
            "num_inference_steps": generation_params.get("steps", Config.DEFAULT_STEPS),
            "guidance_scale": generation_params.get("guidance_scale", Config.DEFAULT_GUIDANCE_SCALE),
        }

        # Add scheduler if supported by the model
        if "scheduler" in generation_params:
            params["scheduler"] = generation_params["scheduler"]

        print(f"🎨 Generating {variations} variations...")
        print(f"📝 Prompt: {prompt_data['prompt'][:100]}...")
        print(f"🤖 Model: {model_name}")

        try:
            # Run the model
            output = replicate.run(
                model_name,
                input=params
            )

            # Download generated images
            generated_paths = []

            # Handle different output formats from different models
            if isinstance(output, list):
                urls = output
            else:
                # Some models return a single URL or iterator
                urls = [output] if isinstance(output, str) else list(output)

            for idx, url in enumerate(urls[:variations], 1):
                print(f"⬇️  Downloading variation {idx}/{len(urls)}...")

                # Download the image
                response = requests.get(url)
                response.raise_for_status()

                # Save to file
                output_path = originals_dir / f"variant-{idx}.png"
                with open(output_path, 'wb') as f:
                    f.write(response.content)

                generated_paths.append(output_path)
                print(f"✅ Saved: {output_path}")

            # Save metadata
            self._save_metadata(
                output_dir,
                subject=subject,
                style=style,
                prompt=prompt_data["prompt"],
                negative_prompt=prompt_data["negative_prompt"],
                model=model_name,
                variations=len(generated_paths),
                params=params,
                format=format,
                aspect_ratio=aspect_ratio if format == "instagram" else None
            )

            return generated_paths

        except Exception as e:
            print(f"❌ Error generating icons: {e}")

            # Try alternative model if primary fails
            if model is None and model_name == Config.DEFAULT_MODEL:
                print(f"🔄 Trying alternative model...")
                return self.generate(
                    subject=subject,
                    style=style,
                    variations=variations,
                    color=color,
                    output_dir=output_dir,
                    model=Config.ALTERNATIVE_MODEL,
                    **generation_params
                )
            raise

    def _save_metadata(
        self,
        output_dir: Path,
        subject: str,
        style: str,
        prompt: str,
        negative_prompt: str,
        model: str,
        variations: int,
        params: Dict,
        format: str = "ios",
        aspect_ratio: Optional[str] = None
    ):
        """Save generation metadata to JSON file."""
        import json
        import datetime

        metadata = {
            "generated_at": datetime.datetime.now().isoformat(),
            "subject": subject,
            "style": style,
            "format": format,
            "model": model,
            "variations": variations,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "parameters": params,
        }

        if aspect_ratio:
            metadata["aspect_ratio"] = aspect_ratio

        metadata_path = output_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"📄 Metadata saved: {metadata_path}")

        # Save prompt as plain text file
        prompt_path = output_dir / "prompt.txt"
        with open(prompt_path, 'w') as f:
            f.write(prompt)

        print(f"📝 Prompt saved: {prompt_path}")
