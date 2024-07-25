from typing import Optional, Union
from uuid import UUID

from beanie import Document, Link
from lcax import Assembly as LCAxAssembly
from lcax import EPD as LCAxEPD
from lcax import Product as LCAxProduct
from lcax import Project as LCAxProject
from lcax import TechFlow as LCAxTechFlow
from pydantic import Field


class DBEPD(LCAxEPD, Document):
    id: UUID


class DBTechFlow(LCAxTechFlow, Document):
    id: UUID


# class DBImpactData(Document):
#     epd: Optional[Link[DBEPD]] = Field(default=None, alias="EPD")
#     tech_flow: Optional[Link[DBTechFlow]] = Field(default=None, alias="techFlow")


class DBProduct(LCAxProduct, Document):
    id: UUID
    impact_data: Union[Optional[Link[DBEPD]] | Optional[Link[DBTechFlow]]] = Field(..., alias="impactData")


class DBAssembly(LCAxAssembly, Document):
    id: UUID
    products: list[Link[DBProduct]]


class DBProject(LCAxProject, Document):
    id: UUID
    assemblies: list[Link[DBAssembly]]
