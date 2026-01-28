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

    # Generation Parameters
    DEFAULT_STEPS = 30
    DEFAULT_GUIDANCE_SCALE = 7.0
    DEFAULT_SCHEDULER = "DPM++ 2M SDE Karras"
    DEFAULT_SIZE = 1024
    DEFAULT_VARIATIONS = 4

    # Model Selection
    # Using SDXL as the primary model
    DEFAULT_MODEL = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
    ALTERNATIVE_MODEL = "black-forest-labs/flux-schnell:f2ab8a5569a0d8780f87f3eeb314deeae2fb23c28e207e65ca3dbcf84eb4f6a5"

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
