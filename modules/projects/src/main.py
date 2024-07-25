import logging.config
from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from supertokens_python.recipe.session.exceptions import UnauthorisedError

from core.auth import supertokens_init
from core.config import settings
from core.connection import get_database
from models import DBAssembly, DBProduct, DBEPD, DBTechFlow
from routes import graphql_app

if "test" not in settings.SERVER_NAME.lower():
    logging.config.fileConfig("logging.conf", disable_existing_loggers=False)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from models import DBProject, DBContribution

    db = get_database()
    await init_beanie(
        database=db, document_models=[DBProject, DBAssembly, DBProduct, DBEPD, DBTechFlow, DBContribution]
    )
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
