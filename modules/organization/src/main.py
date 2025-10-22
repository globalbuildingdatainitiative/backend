import logging.config
from contextlib import asynccontextmanager
from pathlib import Path

import yaml
from beanie import init_beanie
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from supertokens_python.recipe.session.exceptions import UnauthorisedError, TryRefreshTokenError

from core.auth import supertokens_init
from core.config import settings
from core.connection import get_database
from core.exceptions import MicroServiceConnectionError
from core.cache import organization_cache

from routes import graphql_app

log_config = yaml.safe_load((Path(__file__).parent / "logging.yaml").read_text())
log_config["loggers"]["main"]["level"] = settings.LOG_LEVEL
logging.config.dictConfig(log_config)

logger = logging.getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    from models import DBOrganization

    db = get_database()
    await init_beanie(database=db, document_models=[DBOrganization])


    # Load organization cache on startup
    
    logger.info("Loading organization cache...")
    await organization_cache.load_all()
    
    # Start periodic reload
    organization_cache.start_periodic_reload()
    
    yield


app = FastAPI(title=settings.SERVER_NAME, openapi_url=f"{settings.API_STR}/openapi.json", lifespan=lifespan)

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


@app.exception_handler(TryRefreshTokenError)
async def refresh_exception_handler(request: Request, exc: TryRefreshTokenError):
    logger.error(exc)

    return JSONResponse(
        status_code=401,
        content={"data": "Access token expired"},
    )


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logger.error(f"Unknown Error {type(exc)} - {exc}")

    return JSONResponse(
        status_code=500,
        content={"data": exc},
    )


@app.exception_handler(MicroServiceConnectionError)
async def microservice_exception_handler(request: Request, exc: MicroServiceConnectionError):
    logger.error(exc)

    return JSONResponse(
        status_code=501,
        content={"data": exc.message},
    )
