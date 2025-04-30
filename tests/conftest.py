# tests/conftest.py
import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# We need to patch the Settings class before it's imported
# First, identify the module path of the Settings class
SETTINGS_MODULE = "app.core.config"

# Mock the Settings class
class MockSettings:
    """A fake settings class that provides all required attributes."""
    
    def __init__(self, **kwargs):
        # Set default values for all required settings
        self.PROJECT_NAME = os.environ.get("PROJECT_NAME", "Test Project")
        self.API_V1_STR = "/api/v1"
        
        # Database settings
        self.POSTGRES_SERVER = os.environ.get("POSTGRES_SERVER", "mock")
        self.POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
        self.POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
        self.POSTGRES_DB = os.environ.get("POSTGRES_DB", "postgres")
        self.SQLALCHEMY_DATABASE_URI = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        
        # Broker settings
        self.BROKER_USER = os.environ.get("BROKER_USER", "guest")
        self.BROKER_PASSWORD = os.environ.get("BROKER_PASSWORD", "guest")
        self.BROKER_HOST = os.environ.get("BROKER_HOST", "localhost")
        self.BROKER_PORT = os.environ.get("BROKER_PORT", "5672")
        self.BROKER_VHOST = os.environ.get("BROKER_VHOST", "/")
        self.CELERY_BROKER_URL = f"amqp://{self.BROKER_USER}:{self.BROKER_PASSWORD}@{self.BROKER_HOST}:{self.BROKER_PORT}/{self.BROKER_VHOST}"
        self.CELERY_RESULT_BACKEND = f"rpc://{self.BROKER_USER}:{self.BROKER_PASSWORD}@{self.BROKER_HOST}:{self.BROKER_PORT}/{self.BROKER_VHOST}"
        
        # ClickHouse settings
        self.CLICKHOUSE_HOST = os.environ.get("CLICKHOUSE_HOST", "mock")
        self.CLICKHOUSE_USERNAME = os.environ.get("CLICKHOUSE_USERNAME", "default")
        self.CLICKHOUSE_PASSWORD = os.environ.get("CLICKHOUSE_PASSWORD", "mock_password")
        self.CLICKHOUSE_DATABASE = os.environ.get("CLICKHOUSE_DATABASE", "default")
        
        # Monitoring settings
        self.JAEGER_URL = os.environ.get("JAEGER_URL", "http://localhost:14268/api/traces")
        
        # Admin user settings
        self.SUPER_ADMIN_EMAIL = os.environ.get("SUPER_ADMIN_EMAIL", "admin@example.com")
        self.SUPER_ADMIN_USERNAME = os.environ.get("SUPER_ADMIN_USERNAME", "admin")
        self.SUPER_ADMIN_PASSWORD = os.environ.get("SUPER_ADMIN_PASSWORD", "admin")
        
        # Add any additional settings your app might need
        # Set all values passed through kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

# Apply patches before any imports occur
def pytest_configure(config):
    """Configure test environment before any modules are loaded."""
    # Set all required environment variables
    required_env_vars = {
        "PROJECT_NAME": "Test Project",
        "POSTGRES_SERVER": "mock",
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "postgres",
        "POSTGRES_DB": "postgres",
        "BROKER_USER": "guest",
        "BROKER_PASSWORD": "guest",
        "BROKER_HOST": "localhost",
        "BROKER_PORT": "5672",
        "BROKER_VHOST": "/",
        "CLICKHOUSE_HOST": "mock",
        "CLICKHOUSE_USERNAME": "default",
        "CLICKHOUSE_PASSWORD": "mock_password",
        "CLICKHOUSE_DATABASE": "default",
        "JAEGER_URL": "http://localhost:14268/api/traces",
        "SUPER_ADMIN_EMAIL": "admin@example.com",
        "SUPER_ADMIN_USERNAME": "admin",
        "SUPER_ADMIN_PASSWORD": "admin",
    }
    
    # Set all environment variables
    for key, value in required_env_vars.items():
        os.environ[key] = value
    
    # Create mock settings instance
    mock_settings = MockSettings()
    
    # Mock modules that might connect to external services
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
    
    # Create a patch for app.core.config.Settings
    patcher = patch(f"{SETTINGS_MODULE}.Settings", MockSettings)
    patcher.start()
    
    # Create a patch for app.core.config.settings
    settings_patcher = patch(f"{SETTINGS_MODULE}.settings", mock_settings)
    settings_patcher.start()

# Set up mocking for connections
@pytest.fixture(autouse=True)
def mock_external_connections(monkeypatch):
    """Mock all external connections."""
    # Mock SQLAlchemy
    monkeypatch.setattr("sqlalchemy.create_engine", MagicMock())
    monkeypatch.setattr("sqlalchemy.ext.asyncio.create_async_engine", MagicMock())
    
    # Mock asyncpg connections if module exists
    if "asyncpg" in sys.modules:
        monkeypatch.setattr("asyncpg.connect", MagicMock())
        monkeypatch.setattr("asyncpg.create_pool", MagicMock())
    
    # Mock Celery if module exists
    if "celery" in sys.modules:
        monkeypatch.setattr("celery.Celery", MagicMock())
    
    # Mock clickhouse-connect if module exists
    if "clickhouse_connect" in sys.modules:
        monkeypatch.setattr("clickhouse_connect.get_client", MagicMock(return_value=MagicMock()))

# Example async fixture
@pytest.fixture
async def async_fixture():
    return "async_value"
