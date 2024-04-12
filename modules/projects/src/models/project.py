from uuid import UUID, uuid4

import strawberry
from beanie import Document
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str


class DBProject(ProjectBase, Document):
    pass


@strawberry.experimental.pydantic.type(model=ProjectBase, all_fields=True, name="Project")
class GraphQLProject:
    pass
