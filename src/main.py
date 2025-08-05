from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .api import router as api_router
from .db import engine
from .models import Base

app = FastAPI()

app.include_router(api_router, prefix="/api")

@app.exception_handler(RuntimeError)
async def runtime_error_exception_handler(request: Request, exc: RuntimeError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )

# Инициализация БД при старте
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
