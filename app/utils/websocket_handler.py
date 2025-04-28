from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import AppLogger

logger = AppLogger().get_logger()

class WebSocketHandler:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

    async def send_message(self, message: str):
        await self.websocket.send_text(message)

