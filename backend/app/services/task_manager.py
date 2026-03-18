import uuid
from typing import Optional, Dict, Any
from datetime import datetime

# In-memory store: task_id -> task_data
_tasks: Dict[str, Dict[str, Any]] = {}


class TaskManager:
    def create_task(self, user_input: str, conversation_history: list = None) -> str:
        task_id = str(uuid.uuid4())
        _tasks[task_id] = {
            "task_id": task_id,
            "status": "pending",
            "user_input": user_input,
            "conversation_history": conversation_history or [],
            "created_at": datetime.utcnow().isoformat(),
            "progress": 0,
            "current_step": "Initializing...",
            "result": None,
            "error": None
        }
        return task_id

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return _tasks.get(task_id)

    def update_task(
        self,
        task_id: str,
        status: Optional[str] = None,
        progress: Optional[int] = None,
        current_step: Optional[str] = None,
        result: Optional[Dict] = None,
        error: Optional[str] = None
    ):
        task = _tasks.get(task_id)
        if not task:
            return
        if status:
            task["status"] = status
        if progress is not None:
            task["progress"] = progress
        if current_step:
            task["current_step"] = current_step
        if result:
            task["result"] = result
        if error:
            task["error"] = error
        task["updated_at"] = datetime.utcnow().isoformat()
