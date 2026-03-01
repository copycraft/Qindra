# main.py
from fastapi import FastAPI
from app.management.router import router as management_router
from app.core.db import init_db

app = FastAPI(title="Qindra - Management API")

app.include_router(management_router)

@app.on_event("startup")
def startup():
    init_db()
    print("DB ready")