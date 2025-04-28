import asyncio
from fastapi import APIRouter, WebSocket, HTTPException
from starlette.websockets import WebSocketDisconnect
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.logging import AppLogger

logger = AppLogger().get_logger()

router = APIRouter()


class WebSocketManager:
    def __init__(self, websocket: WebSocket, db: AsyncSession):
        self.websocket = websocket
        self.db = db
        self.audio_data = bytearray()
        self.params: Dict[str, Any] = {}

    async def receive_parameters(self) -> None:
        self.params = await self.websocket.receive_json()
        await self.authenticate_user()
        self._validate_parameters()

    def _validate_parameters(self) -> None:
        required_params = ["bot_id", "number_of_similar_results", "language", "token"]
        missing_params = [param for param in required_params if not self.params.get(param)]

        if missing_params:
            raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")

    async def receive_audio_data(self, timeout: int = 10) -> None:
        try:
            while True:
                try:
                    data = await asyncio.wait_for(self.websocket.receive_bytes(), timeout=timeout)
                    logger.info(f"Received {len(data)} bytes of audio data")
                    self.audio_data.extend(data)
                except asyncio.TimeoutError:
                    logger.warning(f"No data received for {timeout} seconds")
                    break
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected")

    async def process_data(self) -> None:
        """TODO: Implement data processing logic."""
        pass


    async def authenticate_user(self) -> None:
        """Authenticate user using token from params"""
        try:
            token = self.params.get("token")
            if not token:
                raise HTTPException(status_code=401, detail="Token not found")

            self.user = await get_current_user(token, self.db)
            logger.info(f"User {self.user.id} authenticated successfully")
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise HTTPException(status_code=401, detail="Authentication failed")
