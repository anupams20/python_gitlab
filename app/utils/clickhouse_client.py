# app/utils/clickhouse_client.py
# Create this file to provide a configurable mockable client
import os
from unittest.mock import MagicMock

# Import conditionally to allow mocking in tests
try:
    import clickhouse_connect
    has_clickhouse = True
except ImportError:
    has_clickhouse = False

# Create a mock client for testing or initialize a real one
def get_clickhouse_client():
    """Get a ClickHouse client instance or mock."""
    host = os.getenv("CLICKHOUSE_HOST", "clickhouse")
    
    # If in test environment or mock is specified, return mock
    if host == "mock" or not has_clickhouse:
        return MagicMock()
    
    # Return actual client for normal operation
    return clickhouse_connect.get_client(
        host=host,
        port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
        username=os.getenv("CLICKHOUSE_USER", "default"),
        password=os.getenv("CLICKHOUSE_PASSWORD", ""),
        database=os.getenv("CLICKHOUSE_DB", "default"),
    )

# Create a singleton client instance
client = get_clickhouse_client()
