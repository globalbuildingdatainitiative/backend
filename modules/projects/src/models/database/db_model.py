import datetime
from typing import Optional, Union
from uuid import UUID, uuid4

from beanie import Document, Link, BackLink
from lcax import Assembly as LCAxAssembly
from lcax import EPD as LCAxEPD
from lcax import Product as LCAxProduct
from lcax import Project as LCAxProject
from lcax import TechFlow as LCAxTechFlow
from pydantic import Field, BaseModel

from ..project_state import ProjectState


class ContributionBase(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    uploaded_at: datetime.datetime = Field(default_factory=datetime.datetime.now, alias="uploadedAt")
    user_id: UUID = Field(alias="userId")
    organization_id: UUID = Field(alias="organizationId")
    public: bool = Field(default=False)


class DBContribution(ContributionBase, Document):
    project: Link["DBProject"]


class DBEPD(LCAxEPD, Document):
    id: UUID


class DBTechFlow(LCAxTechFlow, Document):
    id: UUID


class DBProduct(LCAxProduct, Document):
    id: UUID
    impact_data: Union[Optional[Link[DBEPD]] | Optional[Link[DBTechFlow]]] = Field(..., alias="impactData")


class DBAssembly(LCAxAssembly, Document):
    id: UUID
    products: list[Link[DBProduct]]


class DBProject(LCAxProject, Document):
    id: UUID
    assemblies: list[Link[DBAssembly]]
    contribution: BackLink[DBContribution] = Field(original_field="project")

    # State management fields
    state: ProjectState = Field(default=ProjectState.DRAFT)
    created_by: UUID = Field(alias="createdBy")
    assigned_to: Optional[UUID] = Field(default=None, alias="assignedTo")
    assigned_at: Optional[datetime.datetime] = Field(default=None, alias="assignedAt")
    previous_state: Optional[str] = Field(default=None)
