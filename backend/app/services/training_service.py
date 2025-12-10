"""
Training Service - Manages background model training jobs

Handles:
- Job creation and tracking
- Background training execution
- Progress updates
- Result storage
"""

import threading
import uuid
from datetime import datetime
from typing import Dict, Optional, Callable
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TrainingJob:
    """Represents a training job"""
    
    def __init__(self, job_id: str, model_name: str):
        self.job_id = job_id
        self.model_name = model_name
        self.status = JobStatus.PENDING
        self.progress = 0
        self.current_step = "Initializing..."
        self.started_at = datetime.utcnow()
        self.completed_at = None
        self.metrics = None
        self.error = None
        
    def to_dict(self) -> dict:
        """Convert to dictionary for API response"""
        return {
            'job_id': self.job_id,
            'model_name': self.model_name,
            'status': self.status,
            'progress': self.progress,
            'current_step': self.current_step,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'metrics': self.metrics,
            'error': self.error
        }


class TrainingService:
    """Service to manage model training jobs"""
    
    def __init__(self):
        self.jobs: Dict[str, TrainingJob] = {}
        self.lock = threading.Lock()
        self.active_job = None  # Only one training job at a time (MVP)
        
    def create_job(self, model_name: str) -> str:
        """
        Create a new training job
        
        Args:
            model_name: Name of model to train
            
        Returns:
            job_id
        """
        # Check if there's already an active job
        with self.lock:
            if self.active_job and self.jobs[self.active_job].status == JobStatus.RUNNING:
                raise ValueError("Another training job is already running. Please wait for it to complete.")
        
        # Generate unique job ID
        job_id = f"train_{model_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Create job
        job = TrainingJob(job_id, model_name)
        
        with self.lock:
            self.jobs[job_id] = job
            
        return job_id
    
    def get_job(self, job_id: str) -> Optional[TrainingJob]:
        """Get job by ID"""
        return self.jobs.get(job_id)
    
    def list_jobs(self, limit: int = 10) -> list:
        """List recent jobs"""
        jobs = sorted(
            self.jobs.values(),
            key=lambda j: j.started_at,
            reverse=True
        )
        return [j.to_dict() for j in jobs[:limit]]
    
    def update_progress(self, job_id: str, progress: int, step: str):
        """Update job progress"""
        job = self.jobs.get(job_id)
        if job:
            with self.lock:
                job.progress = progress
                job.current_step = step
    
    def mark_running(self, job_id: str):
        """Mark job as running"""
        job = self.jobs.get(job_id)
        if job:
            with self.lock:
                job.status = JobStatus.RUNNING
                self.active_job = job_id
    
    def mark_completed(self, job_id: str, metrics: dict):
        """Mark job as completed"""
        job = self.jobs.get(job_id)
        if job:
            with self.lock:
                job.status = JobStatus.COMPLETED
                job.progress = 100
                job.current_step = "Training completed successfully!"
                job.completed_at = datetime.utcnow()
                job.metrics = metrics
                if self.active_job == job_id:
                    self.active_job = None
    
    def mark_failed(self, job_id: str, error: str):
        """Mark job as failed"""
        job = self.jobs.get(job_id)
        if job:
            with self.lock:
                job.status = JobStatus.FAILED
                job.current_step = "Training failed"
                job.completed_at = datetime.utcnow()
                job.error = error
                if self.active_job == job_id:
                    self.active_job = None
    
    def start_training_background(self, job_id: str, training_func: Callable):
        """
        Start training in background thread
        
        Args:
            job_id: Job ID
            training_func: Function to execute (should accept job_id and service)
        """
        thread = threading.Thread(
            target=training_func,
            args=(job_id, self),
            daemon=True
        )
        thread.start()


# Global service instance
_training_service = None


def get_training_service() -> TrainingService:
    """Get or create global training service instance"""
    global _training_service
    
    if _training_service is None:
        _training_service = TrainingService()
    
    return _training_service
