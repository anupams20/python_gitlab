from typing import Optional

from pydantic import BaseModel


class TaskOut(BaseModel):
    id: str
    status: Optional[str] = None
    result: Optional[dict] = None
    state: Optional[str] = None
    args: Optional[str] = None
    retries: Optional[str] = None
    info: Optional[str] = None
