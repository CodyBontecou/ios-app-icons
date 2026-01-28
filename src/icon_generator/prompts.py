"""Prompt templates and management for different icon styles."""

from typing import Dict, Optional

class PromptTemplate:
    """Base class for prompt templates."""

    def __init__(self, positive_template: str, negative_prompt: str = ""):
        self.positive_template = positive_template
        self.negative_prompt = negative_prompt

    def format(self, subject: str, **kwargs) -> Dict[str, str]:
        """Format the template with the given subject and parameters."""
        positive = self.positive_template.format(subject=subject, **kwargs)
        return {
            "prompt": positive,
            "negative_prompt": self.negative_prompt
        }


class IconPrompts:
    """Collection of prompt templates for different icon styles."""

    # iOS Style - rounded, modern app icon
    IOS_TEMPLATE = PromptTemplate(
        positive_template=(
            "app icon, iOS app icon, {subject}, {style}, "
            "rounded corners, gradient background, modern design, "
            "clean, professional, high quality, centered composition, "
            "simple, minimalist, digital art"
        ),
        negative_prompt=(
            "text, letters, words, watermark, signature, blurry, "
            "low quality, distorted, ugly, deformed, realistic photo, "
            "complex background, cluttered"
        )
    )

    # Flat Style - minimalist flat design
    FLAT_TEMPLATE = PromptTemplate(
        positive_template=(
            "flat icon design, {subject}, {color} background, "
            "minimalist, simple shapes, solid colors, vector style, "
            "2D design, clean lines, modern, professional"
        ),
        negative_prompt=(
            "3D, realistic, shadows, gradients, texture, "
            "text, letters, watermark, complex, detailed, photo"
        )
    )

    # Vector Style - illustration style
    VECTOR_TEMPLATE = PromptTemplate(
        positive_template=(
            "{subject}, vector illustration, smooth curves, "
            "clean lines, vibrant colors, professional icon design, "
            "simple composition, centered, high quality vector art"
        ),
        negative_prompt=(
            "realistic, photo, 3D render, text, watermark, "
            "blurry, low quality, complex background"
        )
    )

    # Custom Style - fully customizable prompt
    CUSTOM_TEMPLATE = PromptTemplate(
        positive_template="{custom_style}",
        negative_prompt=(
            "text, letters, words, watermark, signature, blurry, "
            "low quality, distorted, ugly, deformed"
        )
    )

    STYLE_MAP = {
        "ios": IOS_TEMPLATE,
        "flat": FLAT_TEMPLATE,
        "vector": VECTOR_TEMPLATE,
        "custom": CUSTOM_TEMPLATE,
    }

    @classmethod
    def get_template(cls, style: str) -> PromptTemplate:
        """Get a prompt template by style name."""
        if style not in cls.STYLE_MAP:
            raise ValueError(
                f"Unknown style '{style}'. "
                f"Available styles: {', '.join(cls.STYLE_MAP.keys())}"
            )
        return cls.STYLE_MAP[style]

    @classmethod
    def build_prompt(
        cls,
        subject: str,
        style: str = "ios",
        color: Optional[str] = None,
        extra_style: str = "modern, colorful",
        custom_style: Optional[str] = None
    ) -> Dict[str, str]:
        """Build a complete prompt for the given parameters."""
        template = cls.get_template(style)

        kwargs = {
            "style": extra_style,
            "color": color or "gradient"
        }

        # If using custom style, pass the full custom prompt
        if style == "custom" and custom_style:
            kwargs["custom_style"] = custom_style

        return template.format(subject, **kwargs)

    @classmethod
    def enhance_subject(cls, subject: str) -> str:
        """Enhance the subject description for better results."""
        # Basic enhancement - can be expanded
        subject = subject.strip()

        # Add "icon of" prefix if not present
        if not any(subject.lower().startswith(prefix) for prefix in ["icon of", "a ", "an ", "the "]):
            if subject[0].lower() in 'aeiou':
                subject = f"an {subject}"
            else:
                subject = f"a {subject}"

        return subject
