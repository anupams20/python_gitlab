from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException

from app.celery.tasks import sample_task
from app.schema.task import TaskOut

router = APIRouter()


@router.get("/{x}/{y}")
async def test_sample_task(x: int, y: int):
    task = sample_task.delay(x, y)
    return TaskOut(id=task.id, status=task.status if task.status else None, state=task.state if task.state else None,
                   retries=str(task.retries) if task.retries else None, info=str(task.info) if task.info else None)


@router.post("/{task_id}/status")
async def task_status(task_id: str):
    task = AsyncResult(task_id)
    response = TaskOut(id=task.id, status=task.status if task.status else None,
                       result=task.result if task.result else None, state=task.state if task.state else None,
                       args=task.args if task.args else None, retries=str(task.retries) if task.retries else None,
                       info=str(task.info) if task.info else None)
    if task.state == 'FAILURE':
        raise HTTPException(status_code=500, detail=response.model_dump())
    return response
