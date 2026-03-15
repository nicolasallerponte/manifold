from __future__ import annotations

import asyncio
import json
import logging
import threading
from typing import Any

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("manifold")


class ConnectionManager:
    def __init__(self):
        self._clients: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        async with self._lock:
            self._clients.append(ws)
        logger.info(f"Client connected. Total: {len(self._clients)}")

    async def disconnect(self, ws: WebSocket):
        async with self._lock:
            self._clients = [c for c in self._clients if c != ws]
        logger.info(f"Client disconnected. Total: {len(self._clients)}")

    async def broadcast(self, data: dict):
        message = json.dumps(data, default=_json_safe)
        dead = []
        for client in self._clients:
            try:
                await client.send_text(message)
            except Exception:
                dead.append(client)
        for d in dead:
            await self.disconnect(d)


def _json_safe(obj: Any):
    """Fallback serializer for non-standard types."""
    if hasattr(obj, "item"):
        return obj.item()
    if hasattr(obj, "tolist"):
        return obj.tolist()
    return str(obj)


def _build_app(manager: ConnectionManager) -> FastAPI:
    app = FastAPI(title="manifold", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health():
        return {"status": "ok", "clients": len(manager._clients)}

    @app.websocket("/ws")
    async def websocket_endpoint(ws: WebSocket):
        await manager.connect(ws)
        try:
            while True:
                await ws.receive_text()  # keep-alive
        except WebSocketDisconnect:
            await manager.disconnect(ws)

    return app


class ManifoldServer:
    """
    Runs a FastAPI + WebSocket server in a background thread.
    Receives metric dicts from hooks and broadcasts to all dashboard clients.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 7331):
        self.host = host
        self.port = port
        self._manager = ConnectionManager()
        self._app = _build_app(self._manager)
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None

    def start(self):
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info(f"manifold dashboard → http://{self.host}:{self.port}")

    def _run(self):
        asyncio.set_event_loop(self._loop)
        config = uvicorn.Config(
            self._app,
            host=self.host,
            port=self.port,
            loop="asyncio",
            log_level="warning",
        )
        server = uvicorn.Server(config)
        self._loop.run_until_complete(server.serve())

    def emit(self, step: int, metrics: dict):
        """Called from the hook callback (training thread)."""
        if self._loop is None:
            return
        asyncio.run_coroutine_threadsafe(
            self._manager.broadcast({"step": step, "metrics": metrics}),
            self._loop,
        )

    def stop(self):
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)


_default_server: ManifoldServer | None = None


def get_server(host: str = "127.0.0.1", port: int = 7331) -> ManifoldServer:
    """Returns (and lazily starts) the global ManifoldServer instance."""
    global _default_server
    if _default_server is None:
        _default_server = ManifoldServer(host=host, port=port)
        _default_server.start()
    return _default_server


def cli():
    """Entrypoint for `manifold` CLI command — starts the server standalone."""
    import argparse

    parser = argparse.ArgumentParser(description="manifold dashboard server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7331)
    args = parser.parse_args()

    server = ManifoldServer(host=args.host, port=args.port)
    server.start()
    print(f"manifold running on http://{args.host}:{args.port}")
    try:
        server._thread.join()
    except KeyboardInterrupt:
        server.stop()