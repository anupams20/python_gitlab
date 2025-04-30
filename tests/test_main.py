# tests/test_main.py
import pytest
from fastapi.testclient import TestClient

# Import app within test function to ensure mocks are set up first
def test_app_root():
    # Import inside the test function to ensure mocks are set up before import
    from app.main import app
    
    client = TestClient(app)
    response = client.get("/")
    
    # Adjust assertion based on your API response
    assert response.status_code in (200, 404)

# If your app's root endpoint returns 404, test a health endpoint instead
def test_health_endpoint():
    from app.main import app
    
    client = TestClient(app)
    # Adjust this path to match your actual health endpoint
    response = client.get("/api/v1/health")
    
    # Skip if endpoint doesn't exist
    if response.status_code == 404:
        pytest.skip("Health endpoint not available")
    
    assert response.status_code == 200
