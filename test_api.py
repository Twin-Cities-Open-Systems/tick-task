#!/usr/bin/env python3
"""
Quick API testing script using FastAPI TestClient.
Run this to test API endpoints without starting a server.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastapi.testclient import TestClient

from tick_task.main import create_application


def test_api():
    """Test API endpoints using TestClient."""
    print("🧪 Testing FIN-tasks API endpoints...")

    # Create test app
    app = create_application()
    client = TestClient(app)

    # Test health endpoint
    print("\n🏥 Testing /api/v1/health:")
    try:
        response = client.get("/api/v1/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.text}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

    # Test tasks endpoint
    print("\n📋 Testing /api/v1/tasks:")
    try:
        response = client.get("/api/v1/tasks")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Tasks endpoint working")
            data = response.json()
            print(f"Found {len(data.get('tasks', []))} tasks")
            print(f"Response: {data}")
        else:
            print(f"❌ Tasks endpoint failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Tasks endpoint error: {e}")

    # Test root endpoint
    print("\n🏠 Testing root endpoint (/):")
    try:
        response = client.get("/")
        print(f"Status: {response.status_code}")
        if response.status_code in [200, 302, 307]:  # Redirects are OK
            print("✅ Root endpoint working")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")


if __name__ == "__main__":
    test_api()
