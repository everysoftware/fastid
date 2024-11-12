from fastapi.testclient import TestClient

from app.runner.api import app

api_client = TestClient(app)
