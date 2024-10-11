from fastapi import FastAPI

from .choices import router as choices_router
from .questions import router as questions_router
from .user import router as user_router

__all__ = ("register_routers",)


def register_routers(app: FastAPI):
    app.include_router(questions_router)
    app.include_router(choices_router)
    app.include_router(user_router)
