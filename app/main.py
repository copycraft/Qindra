# main.py
from fastapi import FastAPI

from app.management.router import router as management_router
from app.core.db.db import init_db as init_core_db

app = FastAPI(title="Qindra - Management API")

# include routers
app.include_router(management_router)

from app.student.router import router as student_router
app.include_router(student_router, prefix="/student")

@app.on_event("startup")
def startup():
    init_core_db()
    print("All DBs ready")