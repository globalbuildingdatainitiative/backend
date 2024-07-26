from typing import Union
from uuid import UUID

import strawberry
from iso3166 import countries
from lcax import AreaType as LCAxAreaType
from lcax import Assembly as LCAxAssembly
from lcax import BuildingInfo as LCAxProjectInfo
from lcax import Classification as LCAxClassification
from lcax import Conversion as LCAxConversion
from lcax import EPD as LCAxEPD
from lcax import Location as LCAxLocation
from lcax import Product as LCAxProduct
from lcax import Project as LCAxProject
from lcax import SoftwareInfo as LCAxSoftwareInfo
from lcax import Source as LCAxSource
from lcax import TechFlow as LCAxTechFlow
from lcax import ValueUnit as LCAxValueUnit
from strawberry.scalars import JSON

from models.project.enums import (
    GraphQLUnit,
    GraphQLCountry,
    GraphQLStandard,
    GraphQLSubType,
    GraphQLBuildingType,
    GraphQLBuildingTypology,
    GraphQLGeneralEnergyClass,
    GraphQLRoofType,
    GraphQLImpactCategoryKey,
    GraphQLLifeCycleStage,
    GraphQLProjectPhase,
    GraphQLBuildingModelScope,
)


@strawberry.experimental.pydantic.type(model=LCAxConversion, name="Conversion")
class GraphQLConversion:
    meta_data: strawberry.auto
    to: GraphQLUnit
    value: strawberry.auto


@strawberry.experimental.pydantic.type(model=LCAxSource, name="Source", all_fields=True)
class GraphQLSource:
    pass


@strawberry.experimental.pydantic.type(model=LCAxEPD, name="EPD")
class GraphQLEPD:
    comment: strawberry.auto
    conversions: list[GraphQLConversion] | None = None
    declared_unit: GraphQLUnit
    format_version: strawberry.auto
    id: UUID
    impacts: JSON
    location: GraphQLCountry
    meta_data: JSON
    name: strawberry.auto
    published_date: strawberry.auto
    reference_service_life: strawberry.auto
    source: GraphQLSource | None = None
    standard: GraphQLStandard
    subtype: GraphQLSubType
    valid_until: strawberry.auto
    version: strawberry.auto


@strawberry.experimental.pydantic.type(model=LCAxTechFlow, name="TechFlow")
class GraphQLTechFlow:
    comment: strawberry.auto
    conversions: list[GraphQLConversion] | None = None
    declared_unit: GraphQLUnit
    format_version: strawberry.auto
    id: UUID
    impacts: JSON
    location: GraphQLCountry
    meta_data: JSON
    name: strawberry.auto
    source: GraphQLSource | None = None


@strawberry.experimental.pydantic.type(model=LCAxProduct, name="Product")
class GraphQLProduct:
    description: strawberry.auto
    id: UUID
    impact_data: Union[GraphQLEPD, GraphQLTechFlow]
    meta_data: JSON
    name: strawberry.auto
    quantity: strawberry.auto
    reference_service_life: strawberry.auto
    results: JSON
    unit: GraphQLUnit


@strawberry.experimental.pydantic.type(model=LCAxClassification, name="Classification", all_fields=True)
class GraphQLClassification:
    pass


@strawberry.experimental.pydantic.type(model=LCAxAssembly, name="Assembly")
class GraphQLAssembly:
    classification: list[GraphQLClassification] | None = None
    comment: strawberry.auto
    description: strawberry.auto
    id: UUID
    meta_data: JSON
    name: strawberry.auto
    products: list[GraphQLProduct]
    quantity: strawberry.auto
    results: JSON
    unit: GraphQLUnit


@strawberry.experimental.pydantic.type(model=LCAxLocation, name="Location")
class GraphQLLocation:
    address: strawberry.auto
    city: strawberry.auto
    country: GraphQLCountry

    @strawberry.field
    def country_name(self) -> str:
        return countries.get(self.country.value).name

    @strawberry.field
    async def longitude(self) -> float:
        from models.project.methods import get_coordinates

        location = await get_coordinates(countries.get(self.country.value).name)
        return location.get("longitude", 0.0)

    @strawberry.field
    async def latitude(self) -> float:
        from models.project.methods import get_coordinates

        location = await get_coordinates(countries.get(self.country.value).name)
        return location.get("latitude", 0.0)


@strawberry.experimental.pydantic.type(model=LCAxValueUnit, name="ValueUnit")
class GraphQLValueUnit:
    unit: GraphQLUnit
    value: strawberry.auto


@strawberry.experimental.pydantic.type(model=LCAxAreaType, name="AreaType")
class GraphQLAreaType:
    unit: GraphQLUnit
    value: strawberry.auto
    definition: strawberry.auto


@strawberry.experimental.pydantic.type(model=LCAxProjectInfo, name="ProjectInfo")
class GraphQLProjectInfo:
    building_completion_year: strawberry.auto
    building_footprint: GraphQLValueUnit | None = None
    building_height: GraphQLValueUnit | None = None
    building_mass: GraphQLValueUnit | None = None
    building_model_scope: list[GraphQLBuildingModelScope] | None = None
    building_permit_year: strawberry.auto
    building_type: GraphQLBuildingType
    building_typology: list[GraphQLBuildingTypology]
    building_users: strawberry.auto
    certifications: strawberry.auto
    energy_demand_electricity: strawberry.auto
    energy_demand_heating: strawberry.auto
    energy_supply_electricity: strawberry.auto
    energy_supply_heating: strawberry.auto
    exported_electricity: strawberry.auto
    floors_above_ground: strawberry.auto
    floors_below_ground: strawberry.auto
    frame_type: strawberry.auto
    general_energy_class: GraphQLGeneralEnergyClass
    gross_floor_area: GraphQLAreaType | None = None
    heated_floor_area: GraphQLAreaType | None = None
    local_energy_class: strawberry.auto
    roof_type: GraphQLRoofType


@strawberry.experimental.pydantic.type(model=LCAxSoftwareInfo, name="SoftwareInfo", all_fields=True)
class GraphQLSoftwareInfo:
    pass


@strawberry.experimental.pydantic.type(model=LCAxProject, name="Project")
class GraphQLProject:
    assemblies: list[GraphQLAssembly]
    classification_system: strawberry.auto
    comment: strawberry.auto
    description: strawberry.auto
    format_version: strawberry.auto
    id: UUID
    impact_categories: list[GraphQLImpactCategoryKey]
    lcia_method: strawberry.auto
    life_cycle_stages: list[GraphQLLifeCycleStage]
    location: GraphQLLocation
    meta_data: JSON | None = None
    name: strawberry.auto
    owner: strawberry.auto
    project_info: GraphQLProjectInfo
    project_phase: GraphQLProjectPhase
    reference_study_period: strawberry.auto
    results: JSON | None = None
    software_info: GraphQLSoftwareInfo
