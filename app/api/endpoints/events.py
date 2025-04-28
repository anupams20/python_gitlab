from fastapi import APIRouter, HTTPException, Depends
from app.celery.clickhouse import process_event
from app.schema.events import EventRequest
from app.core.deps import get_current_user
from app.db.models.user import User

router = APIRouter()

@router.post("")
async def submit_event(event_request: EventRequest, user: User = Depends(get_current_user)):
    try:
        # Call the Celery task
        task = process_event.delay(
            event_request.name,
            event_request.payload,
            event_request.timestamp,
            user.organization_id,
            user.id
        )
        return {"status": "submitted", "task_id": task.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit event: {str(e)}")