# tests/conftest.py
import pytest
from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def mock_clickhouse_client(mocker):
    # Mock the get_client function to return a fake client
    mock_client = MagicMock()
    mocker.patch("clickhouse_connect.get_client", return_value=mock_client)
    return mock_client

@pytest.fixture(scope="session", autouse=True)
def setup_env():
    # Check environment variables without loading .env
    assert os.getenv("PROJECT_NAME"), "Project Name not set in the env"

# Remove setup_function fixture unless explicitly needed for custom loop management
# Example async fixture if needed for other tests
@pytest.fixture
async def async_fixture():
    return "async_value"
