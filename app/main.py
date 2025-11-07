from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from .db import SessionLocal, init_db
from . import tasks

app = FastAPI(title="ClipForge API - scaffold")


class EnqueueRequest(BaseModel):
    project_id: str


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}
