"""FastAPI entrypoint. Shared by EC2, Fargate and Lambda (via Web Adapter)."""
from __future__ import annotations

import hashlib
import os
import socket
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field, HttpUrl

from .codec import hash_code
from .storage import Storage, build_storage

APP_STARTED = time.time()
HOSTNAME = socket.gethostname()
PLATFORM = os.environ.get("PLATFORM", "unknown")


class ShortenIn(BaseModel):
    url: HttpUrl = Field(..., description="Target URL to shorten")


class ShortenOut(BaseModel):
    code: str
    url: str
    platform: str
    hostname: str


def build_app(storage: Storage | None = None) -> FastAPI:
    app = FastAPI(title="shortlink", version="1.0.0")
    store = storage or build_storage()

    @app.get("/healthz")
    def healthz():
        return {"ok": True, "platform": PLATFORM, "host": HOSTNAME, "uptime_s": time.time() - APP_STARTED}

    @app.post("/shorten", response_model=ShortenOut)
    def shorten(payload: ShortenIn):
        url = str(payload.url)
        code = hash_code(url)
        if store.get(code) is None:
            store.put(code, url)
        return ShortenOut(code=code, url=url, platform=PLATFORM, hostname=HOSTNAME)

    @app.get("/r/{code}")
    def redirect(code: str):
        rec = store.get(code)
        if rec is None:
            raise HTTPException(status_code=404, detail="not found")
        store.bump(code)
        return RedirectResponse(url=rec.url, status_code=301)

    @app.get("/stats/{code}")
    def stats(code: str):
        rec = store.get(code)
        if rec is None:
            raise HTTPException(status_code=404, detail="not found")
        return {"code": rec.code, "url": rec.url, "created": rec.created, "hits": rec.hits}

    @app.get("/cpu")
    def cpu(rounds: int = 5000):
        """CPU-bound endpoint: repeated SHA-256 rounds. Used to compare compute
        cost across paradigms independent of network or storage."""
        rounds = max(1, min(rounds, 200_000))
        data = b"cs5296-seed"
        for _ in range(rounds):
            data = hashlib.sha256(data).digest()
        return {"rounds": rounds, "digest": data.hex()[:16], "platform": PLATFORM}

    @app.middleware("http")
    async def add_platform_header(request: Request, call_next):
        resp = await call_next(request)
        resp.headers["x-platform"] = PLATFORM
        resp.headers["x-host"] = HOSTNAME
        return resp

    @app.exception_handler(Exception)
    async def on_error(request: Request, exc: Exception):
        return JSONResponse(status_code=500, content={"error": type(exc).__name__})

    return app


app = build_app()
