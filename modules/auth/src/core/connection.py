from sqlmodel import create_engine
from core.config import settings

def create_postgres_engine():
    return create_engine(str(settings.POSTGRES_URI), pool_pre_ping=True, echo=True)