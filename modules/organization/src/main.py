import logging.config

from beanie import init_beanie
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.auth import supertokens_init
from core.config import settings
from core.connection import get_database
from routes import graphql_app

if "test" not in settings.SERVER_NAME.lower():
    logging.config.fileConfig("logging.conf", disable_existing_loggers=False)

logger = logging.getLogger(__name__)

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
    from models import DBProject, DBOrganization

    db = get_database()
    await init_beanie(database=db, document_models=[DBProject, DBContribution])
