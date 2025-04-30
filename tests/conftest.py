# tests/conftest.py
import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Any

# Apply global patches before any app modules are imported
def pytest_configure(config):
    """Configure test environment before any test modules are loaded."""
    # Mock out third-party modules that try to make connections
    modules_to_mock = [
        "clickhouse_connect",
        "clickhouse_driver",
        "asyncpg",
        "celery",
        "celery.app",
    ]
    
    for module_name in modules_to_mock:
        if module_name not in sys.modules:
            sys.modules[module_name] = MagicMock()
    
    # Mock specific functions
    sys.modules["clickhouse_connect"].get_client = MagicMock(return_value=MagicMock())

# Mock Settings class before it's imported
@pytest.fixture(scope="session", autouse=True)
def mock_settings():
    """Mock the Settings class to avoid validation errors."""
    # Create a fake settings object with all required attributes
    mock_settings = MagicMock()
    
    # Add all required attributes
    settings_attrs = [
        "PROJECT_NAME", "API_V1_STR", "POSTGRES_SERVER", "POSTGRES_USER",
        "POSTGRES_PASSWORD", "POSTGRES_DB", "SQLALCHEMY_DATABASE_URI",
        "BROKER_USER", "BROKER_PASSWORD", "BROKER_HOST", "BROKER_PORT",
        "BROKER_VHOST", "CELERY_BROKER_URL", "CELERY_RESULT_BACKEND",
        "CLICKHOUSE_HOST", "CLICKHOUSE_USERNAME", "CLICKHOUSE_PASSWORD",
        "CLICKHOUSE_DATABASE", "JAEGER_URL", "SUPER_ADMIN_EMAIL",
        "SUPER_ADMIN_USERNAME", "SUPER_ADMIN_PASSWORD"
    ]
    
    # Set attributes to test values
    for attr in settings_attrs:
        setattr(mock_settings, attr, f"test_{attr.lower()}")
    
    # Special handling for database URIs
    mock_settings.SQLALCHEMY_DATABASE_URI = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    
    # Apply the patch
    with patch("app.core.config.Settings", return_value=mock_settings):
        with patch("app.core.config.settings", mock_settings):
            yield mock_settings

@pytest.fixture(scope="session", autouse=True)
def setup_env():
    """Setup environment variables for tests."""
    # Ensure critical environment variables are set
    os.environ.setdefault("PROJECT_NAME", "Test Project")
    
    # Database env vars
    os.environ.setdefault("POSTGRES_SERVER", "mock")
    os.environ.setdefault("POSTGRES_USER", "postgres")
    os.environ.setdefault("POSTGRES_PASSWORD", "postgres")
    os.environ.setdefault("POSTGRES_DB", "postgres")
    
    # Broker env vars
    os.environ.setdefault("BROKER_USER", "guest")
    os.environ.setdefault("BROKER_PASSWORD", "guest")
    os.environ.setdefault("BROKER_HOST", "localhost")
    os.environ.setdefault("BROKER_PORT", "5672")
    os.environ.setdefault("BROKER_VHOST", "/")
    
    # ClickHouse env vars
    os.environ.setdefault("CLICKHOUSE_HOST", "mock")
    os.environ.setdefault("CLICKHOUSE_USERNAME", "default")
    os.environ.setdefault("CLICKHOUSE_PASSWORD", "")
    os.environ.setdefault("CLICKHOUSE_DATABASE", "default")
    
    # Other required env vars
    os.environ.setdefault("JAEGER_URL", "http://localhost:14268/api/traces")
    os.environ.setdefault("SUPER_ADMIN_EMAIL", "admin@example.com")
    os.environ.setdefault("SUPER_ADMIN_USERNAME", "admin")
    os.environ.setdefault("SUPER_ADMIN_PASSWORD", "admin")
    
    yield

# Mock database and external connections
@pytest.fixture(autouse=True)
def mock_external_connections(monkeypatch):
    """Mock all external connections."""
    # Mock SQLAlchemy
    monkeypatch.setattr("sqlalchemy.create_engine", MagicMock())
    monkeypatch.setattr("sqlalchemy.ext.asyncio.create_async_engine", MagicMock())
    
    # Mock asyncpg connections
    if "asyncpg" in sys.modules:
        monkeypatch.setattr("asyncpg.connect", MagicMock())
        monkeypatch.setattr("asyncpg.create_pool", MagicMock())
    
    # Mock Celery
    if "celery" in sys.modules:
        monkeypatch.setattr("celery.Celery", MagicMock())

# Example async fixture if needed for other tests
@pytest.fixture
async def async_fixture():
    return "async_value"
