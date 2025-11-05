import logging.config
from contextlib import asynccontextmanager
from pathlib import Path

import yaml
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from supertokens_python.framework.fastapi import get_middleware
from supertokens_python.recipe.session.exceptions import UnauthorisedError, TryRefreshTokenError

from core.auth import supertokens_init
from core.config import settings
from logic.roles import create_roles
from routes import graphql_app
from routes.health import health_router
from core.cache import init_user_cache

log_config = yaml.safe_load((Path(__file__).parent / "logging.yaml").read_text())
log_config["loggers"]["main"]["level"] = settings.LOG_LEVEL
logging.config.dictConfig(log_config)

logger = logging.getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Running lifespan")

    try:
        await create_roles()
    except Exception as e:
        logger.exception(e)

    # Initialize user cache with the correct database URL
    user_cache = init_user_cache(settings.database_url, cache_size=15000)
    logger.info(f"User cache initialized with database URL: {settings.database_url}")

    # Load user cache on startup
    logger.info("Loading user cache...")
    try:
        await user_cache.load_all()
        logger.info("User cache loaded successfully")
        # Start periodic reload task (every 12 hours)
        user_cache.start_periodic_reload()
        logger.info("Auth service ready")
    except Exception as e:
        logger.exception(f"Failed to load user cache: {e}")

    yield


app = FastAPI(title=settings.SERVER_NAME, openapi_url=f"{settings.API_STR}/openapi.json", lifespan=lifespan)
app.add_middleware(get_middleware())
# if "test" not in settings.SERVER_NAME.lower():


supertokens_init()

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        middleware_class=CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(graphql_app, prefix=settings.API_STR)
app.include_router(health_router, prefix=settings.API_STR)


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unknown Error {type(exc)} - {exc}")

    return JSONResponse(
        status_code=500,
        content={"data": exc},
    )


@app.exception_handler(TryRefreshTokenError)
async def refresh_exception_handler(request: Request, exc: TryRefreshTokenError):
    logger.exception(exc)

    return JSONResponse(
        status_code=401,
        content={"data": "Access token expired"},
    )


@app.exception_handler(UnauthorisedError)
async def unauthorised_exception_handler(request: Request, exc: UnauthorisedError):
    logger.exception(exc)

    return JSONResponse(
        status_code=401,
        content={"data": "User not authenticated"},
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    logger.exception(exc)

    return JSONResponse(
        status_code=400,
        content={"data": "Invalid request data"},
    )
