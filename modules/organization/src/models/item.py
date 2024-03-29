from sqlmodel import Field, SQLModel

from models.utils import string_uuid


class Item(SQLModel, table=True):
    id: str = Field(default_factory=string_uuid, primary_key=True, nullable=False)
    name: str
