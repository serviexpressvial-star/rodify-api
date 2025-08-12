import os
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from .db import engine, init_db
from .routers import services, technicians, system

app = FastAPI(title=os.getenv("APP_NAME", "Rodify API (SQLite)"))

@app.on_event("startup")
def on_start():
    init_db()

@app.get("/health")
def health():
    # simple db check
    with Session(engine) as s:
        s.execute(text("select 1"))
    return {"ok": True}

app.include_router(services.router)
app.include_router(technicians.router)
app.include_router(system.router)
