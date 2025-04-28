from pydantic import BaseModel
from datetime import datetime

class EventRequest(BaseModel):
    name: str
    payload: dict
    timestamp: datetime