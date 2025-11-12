from fastapi import FastAPI
from app.routers import (
    questions_router, 
    answers_router
)

app = FastAPI()

app.include_router(questions_router.router, prefix="/api")
app.include_router(answers_router.router, prefix="/api")
