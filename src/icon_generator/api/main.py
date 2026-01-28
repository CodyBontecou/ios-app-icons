"""FastAPI application for iOS App Icon Generator."""

import asyncio
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from .models import (
    GenerateRequest,
    GenerateResponse,
    JobStatusResponse,
    ConfigResponse,
    ErrorResponse,
    JobStatus,
    VariantInfo,
    IconInfo,
)
from .job_queue import job_queue, Job
from ..config import Config
from ..generator import IconGenerator
from ..processor import IconProcessor


# Create FastAPI app
app = FastAPI(
    title="iOS App Icon Generator API",
    description="AI-powered iOS app icon generation using Stable Diffusion",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure output directory exists
Config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files for serving generated icons
app.mount("/output", StaticFiles(directory=str(Config.OUTPUT_DIR)), name="output")


def run_generation(job: Job, base_url: str):
    """Run the generation process synchronously (for background task)."""
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Update status to processing
        loop.run_until_complete(job_queue.update_job(
            job.id,
            status=JobStatus.PROCESSING,
            progress=5,
            message="Initializing generator..."
        ))

        # Validate custom style requirement
        if job.request.style.value == "custom" and not job.request.custom_style:
            raise ValueError("custom_style is required when style is 'custom'")

        # Validate configuration
        Config.validate()

        # Initialize generator
        generator = IconGenerator()

        # Set up output directory
        output_dir = Config.get_output_dir(job.request.subject)

        # Update progress
        loop.run_until_complete(job_queue.update_job(
            job.id,
            progress=10,
            message="Starting AI generation...",
            output_dir=output_dir
        ))

        # Generate icons
        generated_paths = generator.generate(
            subject=job.request.subject,
            style=job.request.style.value,
            variations=job.request.variations,
            color=job.request.color,
            custom_style=job.request.custom_style,
            output_dir=output_dir,
            steps=job.request.steps,
            guidance_scale=job.request.guidance_scale
        )

        # Update progress
        loop.run_until_complete(job_queue.update_job(
            job.id,
            progress=60,
            message=f"Generated {len(generated_paths)} variations. Processing..."
        ))

        # Post-process icons
        originals_dir = output_dir / "originals"

        if job.request.remove_bg or job.request.apply_mask:
            results = IconProcessor.process_generated_icons(
                originals_dir=originals_dir,
                output_base_dir=output_dir,
                remove_bg=job.request.remove_bg,
                apply_mask=job.request.apply_mask
            )
        else:
            results = {}

        # Build variant info for response
        variants = []
        output_dir_name = output_dir.name

        for idx, original_path in enumerate(sorted(originals_dir.glob("variant-*.png")), 1):
            variant_name = original_path.stem
            original_url = f"{base_url}/output/{output_dir_name}/originals/{original_path.name}"

            processed_icons = []
            if variant_name in results:
                for icon_path in results[variant_name]:
                    size = int(icon_path.stem.split("-")[1])
                    icon_url = f"{base_url}/output/{output_dir_name}/processed/{variant_name}/{icon_path.name}"
                    processed_icons.append(IconInfo(
                        size=size,
                        filename=icon_path.name,
                        url=icon_url
                    ))

            variants.append(VariantInfo(
                variant_number=idx,
                original_url=original_url,
                processed_icons=sorted(processed_icons, key=lambda x: -x.size)
            ))

        # Load metadata if available
        metadata = None
        metadata_path = output_dir / "metadata.json"
        if metadata_path.exists():
            import json
            with open(metadata_path) as f:
                metadata = json.load(f)

        # Update job as completed
        loop.run_until_complete(job_queue.update_job(
            job.id,
            status=JobStatus.COMPLETED,
            progress=100,
            message=f"Successfully generated {len(variants)} variants!",
            variants=variants,
            metadata=metadata
        ))

    except Exception as e:
        # Update job as failed
        loop.run_until_complete(job_queue.update_job(
            job.id,
            status=JobStatus.FAILED,
            progress=0,
            message="Generation failed",
            error=str(e)
        ))
    finally:
        loop.close()


@app.post(
    "/generate",
    response_model=GenerateResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def generate_icons(
    request: GenerateRequest,
    background_tasks: BackgroundTasks
) -> GenerateResponse:
    """
    Start an icon generation job.

    Returns a job ID that can be used to check status via GET /status/{job_id}.
    """
    # Validate custom style requirement
    if request.style.value == "custom" and not request.custom_style:
        raise HTTPException(
            status_code=400,
            detail="custom_style is required when style is 'custom'"
        )

    # Create job
    job = await job_queue.create_job(request)

    # Start background generation
    # Use a base URL that works for local development
    base_url = "http://localhost:8000"
    background_tasks.add_task(run_generation, job, base_url)

    return GenerateResponse(
        job_id=job.id,
        status=job.status,
        message="Job created and queued for processing"
    )


@app.get(
    "/status/{job_id}",
    response_model=JobStatusResponse,
    responses={404: {"model": ErrorResponse}}
)
async def get_job_status(job_id: str) -> JobStatusResponse:
    """
    Get the status of a generation job.

    Poll this endpoint to track progress and get results when complete.
    """
    job = await job_queue.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail=f"Job not found: {job_id}"
        )

    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        message=job.message,
        created_at=job.created_at,
        completed_at=job.completed_at,
        subject=job.request.subject,
        style=job.request.style.value,
        variants=job.variants,
        error=job.error,
        metadata=job.metadata
    )


@app.get("/config", response_model=ConfigResponse)
async def get_config() -> ConfigResponse:
    """
    Get configuration and available options.

    Use this to populate UI dropdowns and set default values.
    """
    from .models import IconStyle

    return ConfigResponse(
        styles=[style.value for style in IconStyle],
        ios_icon_sizes=Config.IOS_ICON_SIZES,
        default_steps=Config.DEFAULT_STEPS,
        default_guidance_scale=Config.DEFAULT_GUIDANCE_SCALE,
        default_variations=Config.DEFAULT_VARIATIONS,
        max_variations=8
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    has_token = bool(Config.REPLICATE_API_TOKEN)
    return {
        "status": "healthy",
        "api_configured": has_token
    }


@app.get("/jobs")
async def list_jobs(limit: int = 20):
    """List recent jobs."""
    jobs = await job_queue.list_jobs(limit=limit)
    return {
        "jobs": [
            {
                "job_id": job.id,
                "status": job.status.value,
                "subject": job.request.subject,
                "created_at": job.created_at.isoformat(),
                "completed_at": job.completed_at.isoformat() if job.completed_at else None
            }
            for job in jobs
        ]
    }
