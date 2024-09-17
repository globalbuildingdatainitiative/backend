import logging.config
from pathlib import Path

import yaml
from beanie import init_beanie
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from supertokens_python.recipe.session.exceptions import UnauthorisedError
from core.auth import supertokens_init
from core.config import settings
from core.connection import get_database
from routes import graphql_app

log_config = yaml.safe_load((Path(__file__).parent / "logging.yaml").read_text())
log_config["loggers"]["main"]["level"] = settings.LOG_LEVEL
logging.config.dictConfig(log_config)

logger = logging.getLogger("main")

app = FastAPI(
    title=settings.SERVER_NAME,
    openapi_url=f"{settings.API_STR}/openapi.json",
)

supertokens_init()

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(graphql_app, prefix=settings.API_STR)


@app.on_event("startup")
async def app_init():
    from models import DBOrganization

    db = get_database()
    await init_beanie(database=db, document_models=[DBOrganization])


@app.exception_handler(UnauthorisedError)
async def unauthorised_exception_handler(request: Request, exc: UnauthorisedError):
    logger.error(exc)

    return JSONResponse(
        status_code=401,
        content={"data": "User not authenticated"},
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    logger.error(exc)

    return JSONResponse(
        status_code=400,
        content={"data": "Invalid request data"},
    )
