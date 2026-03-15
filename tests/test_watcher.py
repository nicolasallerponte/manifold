import asyncio
import json
import time

import pytest
from fastapi.testclient import TestClient

from manifold.server.watcher import ManifoldServer, _build_app, ConnectionManager


def test_health_endpoint():
    manager = ConnectionManager()
    app = _build_app(manager)
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_server_starts_and_stops():
    server = ManifoldServer(port=7332)
    server.start()
    time.sleep(0.5)
    assert server._thread.is_alive()
    server.stop()


def test_emit_does_not_crash_without_clients():
    server = ManifoldServer(port=7333)
    server.start()
    time.sleep(0.5)
    server.emit(step=100, metrics={"uniformity": -2.3, "isotropy": 0.8})
    server.stop()