"""Pytest configuration and fixtures for API tests"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture providing a TestClient for the FastAPI application"""
    return TestClient(app)
