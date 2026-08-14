from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.routes import router
from app.core.logging import configure_logging
from app.core.errors import AppError

configure_logging()
app=FastAPI(title="Enterprise AI Software Engineering & Incident Resolution Agent",version="0.1.0")
app.include_router(router)

@app.exception_handler(AppError)
async def app_error(_:Request,exc:AppError):
    return JSONResponse(status_code=exc.status_code,content={"error":{"code":exc.code,"message":exc.message}})
