import asyncio
import os

import pytest
from dotenv import load_dotenv

load_dotenv()

@pytest.mark.asyncio
@pytest.fixture(scope="session", autouse=True)
async def setup_env():
    assert os.getenv("PROJECT_NAME"), "Project Name not set in the env"

@pytest.mark.asyncio
@pytest.fixture(scope="function")
async def setup_function():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()