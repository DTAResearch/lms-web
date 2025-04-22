"""Main module for the LMS backend API."""

from app.api import chat
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from logging import Logger
from app.db.connection import PostgresConnection

from app.api import (
    handle_chat,
    handle_group,
    handle_model,
    handle_rate_limit,
    handle_user,
    handle_knowledge,
    handle_department,
    handle_faculty,
)
from app.api.auth.endpoints import user
from app.api.auth import google
from app.api import handle_iframe

logger = Logger(__name__)
app_conn = PostgresConnection()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5001",
        "https://staging-lms.hoctiep.com",
        "https://lms.hoctiep.com",
        "https://staging-api-lms.hoctiep.com",
    ],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(google.router, tags=["auth"])
app.include_router(user.router, tags=["Auth endpoints"])
app.include_router(handle_chat.router, prefix="/chat", tags=["Chat Handling"])
app.include_router(handle_iframe.router, prefix="/iframe", tags=["Handle Iframe"])
app.include_router(chat.router, tags=["Chat Messages"])
app.include_router(handle_group.router, prefix="/groups", tags=["Handle Groups"])
app.include_router(handle_model.router, prefix="/models", tags=["Handle Models"])
app.include_router(handle_user.router, prefix="/users", tags=["Handle Users"])
app.include_router(
    handle_rate_limit.router, prefix="/rate-limit", tags=["Handle Rate Limit"]
)
app.include_router(
    handle_knowledge.router, prefix="/knowledge", tags=["Handle Knowledge"]
)
app.include_router(
    handle_department.router, prefix="/departments", tags=["Handle Department"]
)
app.include_router(
    handle_faculty.router, prefix="/faculties", tags=["Handle Faculties"]
)


@app.on_event("startup")
async def startup_event():
    logger.info("Start up")
    await app_conn.connect_db()
    app.state.postgres_pool = app_conn.get_session()


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shut down")
    await app_conn.close_db()


@app.middleware("http")
async def dispatch(request: Request, call_next):
    # generate request_id for tracking
    lang = request.headers.get("x-hoctiep-lang", "vi")
    request.state.logger = logger
    # request.state.app_repos = repos
    # request.state.app_usc = usecases
    request.state.postgres_pool = app_conn.get_session()
    request.state.lang = lang

    try:
        response = await call_next(request)
        return response
    except RuntimeError as exc:
        if str(exc) == "No response returned." and await request.is_disconnected():
            return Response(status_code=204)
        raise
