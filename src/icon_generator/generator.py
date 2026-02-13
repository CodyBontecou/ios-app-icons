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
            model: Model to use (sdxl, flux-schnell, flux-dev, flux-pro)
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

        # Get model configuration
        model_key = model or Config.DEFAULT_MODEL
        model_config = Config.get_model_config(model_key)
        model_id = model_config["id"]

        # Determine dimensions based on format
        if format == "instagram":
            width, height = Config.INSTAGRAM_SIZES.get(aspect_ratio, (1080, 1080))
        else:
            width = Config.DEFAULT_SIZE
            height = Config.DEFAULT_SIZE

        # Build parameters based on model capabilities
        params = self._build_model_params(
            model_config=model_config,
            prompt=prompt_data["prompt"],
            negative_prompt=prompt_data["negative_prompt"],
            width=width,
            height=height,
            variations=variations,
            aspect_ratio=aspect_ratio,
            generation_params=generation_params
        )

        print(f"🎨 Generating {variations} variations...")
        print(f"📝 Prompt: {prompt_data['prompt'][:100]}...")
        print(f"🤖 Model: {model_key} ({model_config['description']})")

        try:
            generated_paths = []

            # Handle models that don't support multiple outputs
            if not model_config["supports_num_outputs"]:
                # Generate one at a time
                for i in range(variations):
                    print(f"🔄 Generating variation {i + 1}/{variations}...")
                    output = replicate.run(model_id, input=params)
                    outputs = self._extract_outputs(output)
                    if outputs:
                        path = self._download_image(outputs[0], originals_dir, i + 1)
                        generated_paths.append(path)
            else:
                # Generate all at once
                output = replicate.run(model_id, input=params)
                outputs = self._extract_outputs(output)

                for idx, item in enumerate(outputs[:variations], 1):
                    path = self._download_image(item, originals_dir, idx)
                    generated_paths.append(path)

            # Save metadata
            self._save_metadata(
                output_dir,
                subject=subject,
                style=style,
                prompt=prompt_data["prompt"],
                negative_prompt=prompt_data.get("negative_prompt", ""),
                model=model_key,
                variations=len(generated_paths),
                params=params,
                format=format,
                aspect_ratio=aspect_ratio if format == "instagram" else None
            )

            return generated_paths

        except Exception as e:
            print(f"❌ Error generating icons: {e}")
            raise

    def _build_model_params(
        self,
        model_config: Dict,
        prompt: str,
        negative_prompt: str,
        width: int,
        height: int,
        variations: int,
        aspect_ratio: str,
        generation_params: Dict
    ) -> Dict:
        """Build API parameters based on model capabilities."""
        params = {"prompt": prompt}

        # Add negative prompt if supported
        if model_config["supports_negative_prompt"] and negative_prompt:
            params["negative_prompt"] = negative_prompt

        # Add num_outputs if supported
        if model_config["supports_num_outputs"]:
            params["num_outputs"] = variations

        # Handle size parameters
        if model_config["size_param"] == "width_height":
            params["width"] = width
            params["height"] = height
            params["num_inference_steps"] = generation_params.get(
                "steps", model_config["default_steps"]
            )
        elif model_config["size_param"] == "aspect_ratio":
            # Convert dimensions to aspect ratio string for Flux
            params["aspect_ratio"] = self._get_flux_aspect_ratio(width, height)
            # Flux uses different step parameter names
            if "steps" in generation_params:
                params["num_inference_steps"] = generation_params["steps"]

        # Add guidance scale if model uses it
        if model_config["default_guidance"] > 0:
            params["guidance_scale"] = generation_params.get(
                "guidance_scale", model_config["default_guidance"]
            )

        # Add scheduler if provided and model supports it
        if "scheduler" in generation_params and model_config["supports_negative_prompt"]:
            params["scheduler"] = generation_params["scheduler"]

        # Add output format if specified
        if "output_format" in model_config:
            params["output_format"] = model_config["output_format"]

        return params

    def _get_flux_aspect_ratio(self, width: int, height: int) -> str:
        """Convert width/height to Flux aspect ratio string."""
        ratio = width / height

        # Map to Flux's supported aspect ratios
        if abs(ratio - 1.0) < 0.1:
            return "1:1"
        elif abs(ratio - 16/9) < 0.1:
            return "16:9"
        elif abs(ratio - 9/16) < 0.1:
            return "9:16"
        elif abs(ratio - 4/5) < 0.1:
            return "4:5"
        elif abs(ratio - 5/4) < 0.1:
            return "5:4"
        elif abs(ratio - 4/3) < 0.1:
            return "4:3"
        elif abs(ratio - 3/4) < 0.1:
            return "3:4"
        elif abs(ratio - 3/2) < 0.1:
            return "3:2"
        elif abs(ratio - 2/3) < 0.1:
            return "2:3"
        elif width > height:
            return "16:9"  # Default landscape
        else:
            return "9:16"  # Default portrait

    def _extract_outputs(self, output) -> List:
        """Extract outputs from various model output formats."""
        if isinstance(output, list):
            return output
        elif isinstance(output, (str, bytes)):
            return [output]
        else:
            # Handle iterators and FileOutput objects
            try:
                return list(output)
            except:
                return [output]

    def _download_image(self, output, output_dir: Path, index: int) -> Path:
        """Download/save image from URL or raw bytes."""
        print(f"⬇️  Downloading variation {index}...")

        output_path = output_dir / f"variant-{index}.png"

        # Handle different output types from Replicate
        # FileOutput objects have a 'url' attribute
        if hasattr(output, 'url'):
            url = output.url
            response = requests.get(url)
            response.raise_for_status()
            content = response.content
        elif isinstance(output, bytes):
            content = output
        elif hasattr(output, 'read'):
            content = output.read()
        elif isinstance(output, str) and output.startswith(('http://', 'https://')):
            response = requests.get(output)
            response.raise_for_status()
            content = response.content
        else:
            # Try treating as URL string
            response = requests.get(str(output))
            response.raise_for_status()
            content = response.content

        # Save the content, converting to PNG if needed
        from PIL import Image
        import io

        try:
            # Try to open as image and convert to PNG
            img = Image.open(io.BytesIO(content))
            img.save(output_path, 'PNG')
        except Exception:
            # If PIL fails, save raw content with appropriate extension
            # Check if it's WebP
            if content[:4] == b'RIFF' and content[8:12] == b'WEBP':
                webp_path = output_dir / f"variant-{index}.webp"
                with open(webp_path, 'wb') as f:
                    f.write(content)
                # Try converting with PIL
                img = Image.open(webp_path)
                img.save(output_path, 'PNG')
                webp_path.unlink()
            else:
                # Save as-is
                with open(output_path, 'wb') as f:
                    f.write(content)

        print(f"✅ Saved: {output_path}")
        return output_path

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
