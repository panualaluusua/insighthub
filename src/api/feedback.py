"""Feedback API endpoints for receiving user feedback asynchronously."""
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4
from datetime import datetime
from typing import Dict

from src.models.vector_math import FeedbackType
from src.workers.feedback_worker import enqueue_feedback_event

app = FastAPI(title="InsightHub Feedback API")


class FeedbackRequest(BaseModel):
    content_id: UUID = Field(..., description="UUID of the content item")
    user_id: UUID = Field(..., description="UUID of the user providing feedback")
    feedback_type: FeedbackType

    @validator("feedback_type", pre=True)
    def _coerce_enum(cls, v):  # noqa: D401
        if isinstance(v, FeedbackType):
            return v
        return FeedbackType(v)


@app.post("/api/v1/feedback", status_code=202)
async def submit_feedback(request: FeedbackRequest, background_tasks: BackgroundTasks):
    """Accept feedback and enqueue for async processing (Redis RQ if available)."""
    background_tasks.add_task(enqueue_feedback_event, request.model_dump())
    return {
        "feedback_id": str(uuid4()),
        "status": "accepted",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health", tags=["health"])
async def health_check() -> Dict[str, str]:
    """Lightweight liveness probe for orchestrators & load-balancers."""
    return {"status": "ok"} 