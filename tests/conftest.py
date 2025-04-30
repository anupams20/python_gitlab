# tests/conftest.py
import os
import pytest
from unittest.mock import MagicMock, patch

# Mock clickhouse module globally before any imports
@pytest.fixture(scope="session", autouse=True)
def mock_clickhouse_modules():
    """Mock clickhouse modules at the import level to prevent any connection attempts."""
    modules_to_mock = [
        "clickhouse_connect",
        "clickhouse_connect.get_client",
        "clickhouse_driver",
    ]
    
    # Create module level mocks
    mocks = {}
    for module_name in modules_to_mock:
        mock = MagicMock()
        mocks[module_name] = mock
        
    # Apply patches
    patches = []
    for module_name, mock in mocks.items():
        patcher = patch(module_name, mock)
        patches.append(patcher)
        patcher.start()
        
    # Mock get_client function specifically
    mock_client = MagicMock()
    mocks["clickhouse_connect"].get_client.return_value = mock_client
    
    # Allow test to run
    yield mocks
    
    # Remove patches after tests complete
    for patcher in patches:
        patcher.stop()

@pytest.fixture(scope="session", autouse=True)
def setup_env():
    """Setup environment variables for tests."""
    # Set default environment variables if not present
    os.environ.setdefault("PROJECT_NAME", "Test Project")
    os.environ.setdefault("CLICKHOUSE_HOST", "mock")
    
    # Ensure critical environment variables are set
    assert os.getenv("PROJECT_NAME"), "Project Name not set in the env"
    
    yield

# Example async fixture if needed for other tests
@pytest.fixture
async def async_fixture():
    return "async_value"
