import datetime
from uuid import UUID, uuid4

import strawberry
from beanie import Document, Link
from pydantic import BaseModel, Field

from .project import DBProject, GraphQLProject, GraphQLInputProject


class ContributionBase(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    uploaded_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    user_id: UUID
    organization_id: UUID


class DBContribution(ContributionBase, Document):
    project: Link[DBProject]


@strawberry.experimental.pydantic.type(model=ContributionBase, all_fields=True, name="Contribution")
class GraphQLContribution:
    project: GraphQLProject


@strawberry.input
class InputContribution:
    project: GraphQLInputProject
