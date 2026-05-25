from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
import asyncio
import json
import logging

from app.services.housing_service import HousingAdvisoryService
from app.services.guardrails import check_input
from app.services.risk_engine import evaluate_risk
from app.services.task_manager import TaskManager
from app.api.auth import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

# Issue 7 — Singleton service instance (created once, reused across requests)
_housing_service = None

def get_housing_service() -> HousingAdvisoryService:
    global _housing_service
    if _housing_service is None:
        _housing_service = HousingAdvisoryService()
    return _housing_service

# Issue 2 — In-memory conversation store: session_id -> list of messages
_conversation_store: dict = {}
_MAX_HISTORY = 10
_MAX_FIELD_LENGTH = 500

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
    session_id: str = "default"


class TaskResponse(BaseModel):
    task_id: str
    status: str


def _validate_field_lengths(data: dict) -> str | None:
    """Return an error message if any field exceeds the max length, else None."""
    for field_name in ["location", "destination", "query"]:
        value = data.get(field_name, "")
        if isinstance(value, str) and len(value) > _MAX_FIELD_LENGTH:
            return f"The '{field_name}' field is too long. Please keep it under {_MAX_FIELD_LENGTH} characters."
    return None


@router.post("/housing-recommendations", response_model=TaskResponse)
async def create_housing_recommendation(
    request: HousingRequest, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Returns task_id immediately. AI processing runs in a thread pool."""

    # Issue 3 — Input length validation before any processing
    length_error = _validate_field_lengths(request.model_dump())
    if length_error:
        raise HTTPException(status_code=400, detail=length_error)

    # Issue 2 — Retrieve or create session conversation history
    session_id = request.session_id
    if session_id not in _conversation_store:
        _conversation_store[session_id] = []
    conversation_history = _conversation_store[session_id]

    user_input = (
        f"I'm looking for housing in {request.location}. "
        f"My workplace is in {request.destination}. "
        f"The commute distance is {request.distance}km. "
        f"I plan to return at {request.time}. "
        f"My budget is {request.budget} KES per month. "
        f"I prefer {request.safety} safety tolerance. "
        f"I will be living {request.arrangement}. "
        f"Additional concerns: {request.query}"
    )

    task_id = task_manager.create_task(user_input, conversation_history)

    background_tasks.add_task(
        run_in_threadpool,
        process_housing_task,
        task_id,
        user_input,
        conversation_history,
        request.time,
        request.distance,
        request.arrangement,
        request.safety,
        float(request.budget),
        session_id,
    )

    logger.info(f"Created task {task_id} for session {session_id}")
    return TaskResponse(task_id=task_id, status="pending")


def process_housing_task(
    task_id: str,
    user_input: str,
    conversation_history: list,
    time_of_day: str,
    commute_distance_km: float,
    living_arrangement: str,
    safety_tolerance: str,
    budget_kes: float,
    session_id: str,
):
    """Synchronous — runs in a thread pool, not the event loop."""
    try:
        task_manager.update_task(task_id, status="processing", progress=10, current_step="Starting analysis...")

        # Issue 1 — Guardrails: check input before anything else
        guard = check_input(user_input)
        if not guard["allowed"]:
            logger.info("Guardrail triggered — returning reframe message")
            task_manager.update_task(
                task_id, status="completed", progress=100,
                current_step="Blocked", result={"status": "blocked", "message": guard["message"]}
            )
            return

        task_manager.update_task(task_id, progress=20, current_step="Evaluating situational risk...")

        # Issue 4 — Risk Engine: deterministic scoring before any AI call
        risk_profile = evaluate_risk(
            time_of_day=time_of_day,
            commute_distance_km=commute_distance_km,
            living_arrangement=living_arrangement,
            safety_tolerance=safety_tolerance,
            budget_kes=budget_kes,
        )
        logger.info(f"Risk profile: {risk_profile.level} (score {risk_profile.score})")

        service = get_housing_service()

        task_manager.update_task(task_id, progress=30, current_step="Analyzing requirements...")
        requirements = service.triage_requirements(user_input, conversation_history)

        if requirements.has_all_details:
            task_manager.update_task(task_id, progress=50, current_step="Researching neighborhoods...")

            recommendations = service.research_neighborhoods(requirements, risk_profile)

            task_manager.update_task(task_id, progress=75, current_step="Preparing recommendations...")
            presentation = service.present_recommendations(recommendations, requirements, risk_profile)

            result = {
                "status": "success",
                "risk_profile": {
                    "level": risk_profile.level,
                    "score": risk_profile.score,
                    "factors": risk_profile.factors,
                },
                "requirements": requirements.model_dump(),
                "recommendations": recommendations.model_dump(),
                "message": presentation,
            }
        else:
            task_manager.update_task(task_id, progress=50, current_step="Need more information")
            follow_up = service.gather_missing_details(requirements)

            result = {
                "status": "needs_more_info",
                "requirements": requirements.model_dump(),
                "message": follow_up,
            }

        task_manager.update_task(
            task_id, status="completed", progress=100,
            current_step="Complete", result=result
        )
        logger.info(f"Task {task_id} completed")

        # Issue 2 — Append exchange to conversation history
        if result.get("status") != "blocked":
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": result.get("message", "")})
            if len(conversation_history) > _MAX_HISTORY * 2:
                _conversation_store[session_id] = conversation_history[-(_MAX_HISTORY * 2):]

    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}")
        task_manager.update_task(
            task_id, status="failed", progress=0,
            current_step="Error", error=str(e)
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
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/health")
async def health_check():
    return {"status": "OK", "service": "Housing Safety Advisory Agent"}
