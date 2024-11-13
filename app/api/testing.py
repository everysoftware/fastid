from fastapi import FastAPI
from fastapi.testclient import TestClient

api_client = TestClient(FastAPI())
