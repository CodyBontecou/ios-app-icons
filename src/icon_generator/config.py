"""Configuration management for the icon generator."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for icon generation."""

    # API Configuration
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

    # Database Configuration
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/icongen"
    )

    # Generation Parameters
    DEFAULT_STEPS = 30
    DEFAULT_GUIDANCE_SCALE = 7.0
    DEFAULT_SCHEDULER = "DPM++ 2M SDE Karras"
    DEFAULT_SIZE = 1024
    DEFAULT_VARIATIONS = 4

    # Model Selection
    DEFAULT_MODEL = "sdxl"

    # Available models with their Replicate IDs and configurations
    MODELS = {
        "sdxl": {
            "id": "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            "supports_negative_prompt": True,
            "supports_num_outputs": True,
            "default_steps": 30,
            "default_guidance": 7.0,
            "size_param": "width_height",  # separate width/height params
            "description": "Stable Diffusion XL - good quality, flexible",
        },
        "flux-schnell": {
            "id": "black-forest-labs/flux-schnell",
            "supports_negative_prompt": False,
            "supports_num_outputs": True,
            "default_steps": 4,
            "default_guidance": 0,  # flux-schnell doesn't use guidance
            "size_param": "aspect_ratio",  # uses aspect_ratio param
            "description": "Flux Schnell - fast generation, decent text",
        },
        "flux-dev": {
            "id": "black-forest-labs/flux-dev",
            "supports_negative_prompt": False,
            "supports_num_outputs": True,
            "default_steps": 28,
            "default_guidance": 3.5,
            "size_param": "aspect_ratio",
            "description": "Flux Dev - better quality, good text rendering",
        },
        "flux-pro": {
            "id": "black-forest-labs/flux-1.1-pro",
            "supports_negative_prompt": False,
            "supports_num_outputs": False,  # pro only does 1 at a time
            "default_steps": 25,
            "default_guidance": 3.0,
            "size_param": "aspect_ratio",
            "output_format": "png",  # Request PNG to avoid WebP issues
            "description": "Flux Pro 1.1 - best quality, best text rendering",
        },
    }

    @classmethod
    def get_model_config(cls, model_name: str) -> dict:
        """Get configuration for a specific model."""
        if model_name not in cls.MODELS:
            raise ValueError(
                f"Unknown model '{model_name}'. "
                f"Available models: {', '.join(cls.MODELS.keys())}"
            )
        return cls.MODELS[model_name]

    # iOS Icon Sizes (width x height in pixels)
    IOS_ICON_SIZES = [
        1024,  # App Store
        180,   # iPhone @3x
        120,   # iPhone @2x
        167,   # iPad Pro @2x
        152,   # iPad @2x
        76,    # iPad @1x
        60,    # iPhone Spotlight @3x (not listed but useful)
        40,    # Spotlight @2x
        29,    # Settings @1x
        20,    # Notification @1x
    ]

    # Instagram Sizes (width x height in pixels)
    # Note: dimensions must be divisible by 8 for SDXL model
    INSTAGRAM_SIZES = {
        "square": (1080, 1080),     # Feed posts (1:1)
        "portrait": (1080, 1352),   # ~4:5 ratio, best engagement
        "landscape": (1080, 568),   # ~1.9:1 ratio
        "story": (1080, 1920),      # 9:16 ratio, stories/reels
    }

    # Output Directory
    OUTPUT_DIR = Path("output")

    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        if not cls.REPLICATE_API_TOKEN:
            raise ValueError(
                "REPLICATE_API_TOKEN not found. "
                "Please set it in your .env file or environment variables. "
                "Get your token from: https://replicate.com/account/api-tokens"
            )

    @classmethod
    def get_output_dir(cls, subject: str, timestamp: str = None) -> Path:
        """Get the output directory for a generation session."""
        import datetime
        if timestamp is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Clean subject for directory name
        clean_subject = "".join(c if c.isalnum() or c in ('-', '_') else '_'
                               for c in subject)

        output_path = cls.OUTPUT_DIR / f"{clean_subject}-{timestamp}"
        output_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (output_path / "originals").mkdir(exist_ok=True)
        (output_path / "processed").mkdir(exist_ok=True)

        return output_path
