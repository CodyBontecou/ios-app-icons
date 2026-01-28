"""Job queue and background task management."""

import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any
from concurrent.futures import ThreadPoolExecutor

from .models import JobStatus, GenerateRequest, VariantInfo, IconInfo


class Job:
    """Represents a generation job."""

    def __init__(self, request: GenerateRequest):
        self.id = str(uuid.uuid4())
        self.request = request
        self.status = JobStatus.PENDING
        self.progress = 0
        self.message = "Job queued"
        self.created_at = datetime.now()
        self.completed_at: Optional[datetime] = None
        self.variants: list[VariantInfo] = []
        self.error: Optional[str] = None
        self.output_dir: Optional[Path] = None
        self.metadata: Optional[Dict[str, Any]] = None


class JobQueue:
    """Manages generation jobs with background processing."""

    def __init__(self, max_workers: int = 2):
        self._jobs: Dict[str, Job] = {}
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = asyncio.Lock()

    async def create_job(self, request: GenerateRequest) -> Job:
        """Create a new job and add it to the queue."""
        job = Job(request)
        async with self._lock:
            self._jobs[job.id] = job
        return job

    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID."""
        async with self._lock:
            return self._jobs.get(job_id)

    async def update_job(
        self,
        job_id: str,
        status: Optional[JobStatus] = None,
        progress: Optional[int] = None,
        message: Optional[str] = None,
        variants: Optional[list[VariantInfo]] = None,
        error: Optional[str] = None,
        output_dir: Optional[Path] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Job]:
        """Update job status and progress."""
        async with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None

            if status is not None:
                job.status = status
                if status == JobStatus.COMPLETED or status == JobStatus.FAILED:
                    job.completed_at = datetime.now()

            if progress is not None:
                job.progress = progress

            if message is not None:
                job.message = message

            if variants is not None:
                job.variants = variants

            if error is not None:
                job.error = error

            if output_dir is not None:
                job.output_dir = output_dir

            if metadata is not None:
                job.metadata = metadata

            return job

    async def list_jobs(self, limit: int = 50) -> list[Job]:
        """List recent jobs."""
        async with self._lock:
            jobs = sorted(
                self._jobs.values(),
                key=lambda j: j.created_at,
                reverse=True
            )
            return jobs[:limit]

    def run_in_background(self, func, *args, **kwargs):
        """Run a function in the background thread pool."""
        return self._executor.submit(func, *args, **kwargs)

    async def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Remove jobs older than max_age_hours."""
        now = datetime.now()
        async with self._lock:
            to_remove = []
            for job_id, job in self._jobs.items():
                age = (now - job.created_at).total_seconds() / 3600
                if age > max_age_hours and job.status in (JobStatus.COMPLETED, JobStatus.FAILED):
                    to_remove.append(job_id)

            for job_id in to_remove:
                del self._jobs[job_id]


# Global job queue instance
job_queue = JobQueue()
