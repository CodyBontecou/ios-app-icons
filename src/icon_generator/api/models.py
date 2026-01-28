"""Pydantic models for API requests and responses."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class IconStyle(str, Enum):
    """Available icon styles."""
    IOS = "ios"
    FLAT = "flat"
    VECTOR = "vector"
    CUSTOM = "custom"


class JobStatus(str, Enum):
    """Status of a generation job."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerateRequest(BaseModel):
    """Request model for icon generation."""
    subject: str = Field(..., description="What to generate (e.g., 'happy cat', 'mountain logo')")
    style: IconStyle = Field(default=IconStyle.IOS, description="Icon style to generate")
    custom_style: Optional[str] = Field(default=None, description="Full custom prompt (required when style='custom')")
    variations: int = Field(default=4, ge=1, le=8, description="Number of variations to generate")
    color: Optional[str] = Field(default=None, description="Background color (for flat style)")
    steps: int = Field(default=30, ge=10, le=100, description="Number of inference steps")
    guidance_scale: float = Field(default=7.0, ge=1.0, le=20.0, description="Guidance scale for generation")
    remove_bg: bool = Field(default=False, description="Whether to remove background")
    apply_mask: bool = Field(default=True, description="Whether to apply iOS rounded corner mask")


class GenerateResponse(BaseModel):
    """Response model for icon generation request."""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    message: str = Field(..., description="Status message")


class IconInfo(BaseModel):
    """Information about a generated icon."""
    size: int = Field(..., description="Icon size in pixels")
    filename: str = Field(..., description="Filename of the icon")
    url: str = Field(..., description="URL to access the icon")


class VariantInfo(BaseModel):
    """Information about a generated variant."""
    variant_number: int = Field(..., description="Variant number")
    original_url: str = Field(..., description="URL to original generated image")
    processed_icons: List[IconInfo] = Field(default_factory=list, description="Processed icon sizes")


class JobStatusResponse(BaseModel):
    """Response model for job status check."""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    progress: int = Field(default=0, ge=0, le=100, description="Progress percentage")
    message: str = Field(..., description="Status message")
    created_at: datetime = Field(..., description="Job creation timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Job completion timestamp")
    subject: str = Field(..., description="Generation subject")
    style: str = Field(..., description="Icon style used")
    variants: List[VariantInfo] = Field(default_factory=list, description="Generated variants")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ConfigResponse(BaseModel):
    """Response model for configuration endpoint."""
    styles: List[str] = Field(..., description="Available icon styles")
    ios_icon_sizes: List[int] = Field(..., description="iOS icon sizes generated")
    default_steps: int = Field(..., description="Default inference steps")
    default_guidance_scale: float = Field(..., description="Default guidance scale")
    default_variations: int = Field(..., description="Default number of variations")
    max_variations: int = Field(..., description="Maximum variations allowed")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
