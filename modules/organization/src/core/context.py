from sqlmodel import Session
from strawberry.types import Info


def get_session(info: Info) -> Session:
    return info.context.get("session")
