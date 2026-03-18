from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
import asyncio
import json
import logging

from app.services.housing_service import HousingAdvisoryService
from app.services.task_manager import TaskManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")
task_manager = TaskManager()


class HousingRequest(BaseModel):
    location: str = ""
    destination: str = ""
    distance: float = 1
    time: str = "Day"
    budget: int = 20000
    safety: str = "Medium"
    arrangement: str = "Alone"
    query: str = ""


class TaskResponse(BaseModel):
    task_id: str
    status: str


@router.post("/housing-recommendations", response_model=TaskResponse)
async def create_housing_recommendation(request: HousingRequest, background_tasks: BackgroundTasks):
    """Returns task_id immediately. AI processing runs in a thread pool."""

    user_input = f"""
    I'm looking for housing in {request.location}.
    My workplace is in {request.destination}.
    The commute distance is {request.distance}km.
    I plan to return at {request.time}.
    My budget is {request.budget} KES per month.
    I prefer {request.safety} safety tolerance.
    I will be living {request.arrangement}.
    Additional concerns: {request.query}
    """

    task_id = task_manager.create_task(user_input)

    # run_in_threadpool ensures the synchronous AI calls don't block the event loop
    background_tasks.add_task(run_in_threadpool, process_housing_task, task_id, user_input)

    logger.info(f"Created task {task_id}")
    return TaskResponse(task_id=task_id, status="pending")


def process_housing_task(task_id: str, user_input: str):
    """Synchronous - runs in a thread pool, not the event loop."""
    try:
        task_manager.update_task(task_id, status="processing", progress=10, current_step="🏠 Starting analysis...")

        service = HousingAdvisoryService()

        task_manager.update_task(task_id, progress=25, current_step="📋 Analyzing requirements...")
        requirements = service.triage_requirements(user_input, [])

        if requirements.has_all_details:
            task_manager.update_task(task_id, progress=40, current_step="✅ Requirements complete")

            task_manager.update_task(task_id, progress=50, current_step="🔍 Researching neighborhoods...")
            recommendations = service.research_neighborhoods(requirements)

            task_manager.update_task(task_id, progress=75, current_step="📝 Preparing recommendations...")
            presentation = service.present_recommendations(recommendations, requirements)

            result = {
                "status": "success",
                "requirements": requirements.model_dump(),
                "recommendations": recommendations.model_dump(),
                "message": presentation
            }
        else:
            task_manager.update_task(task_id, progress=50, current_step="❓ Need more information")
            follow_up = service.gather_missing_details(requirements)

            result = {
                "status": "needs_more_info",
                "requirements": requirements.model_dump(),
                "message": follow_up
            }

        task_manager.update_task(
            task_id, status="completed", progress=100,
            current_step="✅ Complete", result=result
        )
        logger.info(f"Task {task_id} completed")

    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}")
        task_manager.update_task(
            task_id, status="failed", progress=0,
            current_step="❌ Error", error=str(e)
        )


@router.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """Get current task status (polling fallback)."""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/tasks/{task_id}/stream")
async def stream_task_progress(task_id: str):
    """Stream task progress via SSE."""

    async def event_generator():
        last_progress = -1

        while True:
            task = task_manager.get_task(task_id)

            if not task:
                yield f"data: {json.dumps({'error': 'Task not found'})}\n\n"
                break

            if task["progress"] != last_progress:
                yield f"data: {json.dumps(task)}\n\n"
                last_progress = task["progress"]

            if task["status"] in ["completed", "failed"]:
                break

            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/health")
async def health_check():
    return {"status": "OK", "service": "Housing Safety Advisory Agent"}
