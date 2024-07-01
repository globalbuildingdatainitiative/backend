from typing import Optional
from uuid import UUID

import strawberry
from lcax import AreaType as LCAxAreaType
from lcax import Assembly as LCAxAssembly
from lcax import BuildingInfo as LCAxBuildingInfo
from lcax import BuildingModelScope as LCAxBuildingModelScope
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
    GraphQLGeneralEnergyClass,
    GraphQLRoofType,
    GraphQLImpactCategoryKey,
    GraphQLLifeCycleStage,
    GraphQLProjectPhase,
    GraphQLBuildingType,
    GraphQLBuildingTypology,
)


@strawberry.experimental.pydantic.input(model=LCAxConversion, name="InputConversion")
class GraphQLInputConversion:
    meta_data: str | None = None
    to: GraphQLUnit
    value: strawberry.auto


@strawberry.experimental.pydantic.input(model=LCAxSource, name="InputSource", all_fields=True)
class GraphQLInputSource:
    pass


@strawberry.experimental.pydantic.input(model=LCAxEPD, name="InputEPD")
class GraphQLInputEPD:
    comment: strawberry.auto
    conversions: list[GraphQLInputConversion] | None = None
    declared_unit: GraphQLUnit
    format_version: strawberry.auto
    id: UUID | None = None
    impacts: JSON
    location: GraphQLCountry
    meta_data: JSON | None = None
    name: strawberry.auto
    published_date: strawberry.auto
    reference_service_life: strawberry.auto
    source: GraphQLInputSource | None = None
    standard: GraphQLStandard
    subtype: GraphQLSubType
    valid_until: strawberry.auto
    version: strawberry.auto


@strawberry.experimental.pydantic.input(model=LCAxTechFlow, name="InputTechFlow")
class GraphQLInputTechFlow:
    comment: strawberry.auto
    conversions: list[GraphQLInputConversion] | None = None
    declared_unit: GraphQLUnit
    format_version: strawberry.auto
    id: UUID | None = None
    impacts: JSON
    location: GraphQLCountry
    meta_data: JSON | None = None
    name: strawberry.auto
    source: GraphQLInputSource | None = None


@strawberry.one_of_input()
class GraphQLInputImpactData:
    epd: GraphQLInputEPD | None = strawberry.field(name="EPD", default=strawberry.UNSET)
    tech_flow: GraphQLInputTechFlow | None = strawberry.UNSET


@strawberry.experimental.pydantic.input(model=LCAxProduct, name="InputProduct")
class GraphQLInputProduct:
    description: strawberry.auto
    id: UUID | None = None
    impact_data: GraphQLInputImpactData
    meta_data: JSON | None = None
    name: strawberry.auto
    quantity: strawberry.auto
    reference_service_life: strawberry.auto
    results: JSON | None = None
    transport: JSON | None = None
    unit: GraphQLUnit


@strawberry.experimental.pydantic.input(model=LCAxClassification, name="InputClassification", all_fields=True)
class GraphQLInputClassification:
    pass


@strawberry.experimental.pydantic.input(model=LCAxAssembly, name="InputAssembly")
class GraphQLInputAssembly:
    category: strawberry.auto
    classification: list[GraphQLInputClassification] | None = None
    comment: strawberry.auto
    description: strawberry.auto
    id: UUID | None = None
    meta_data: JSON | None = None
    name: strawberry.auto
    products: list[GraphQLInputProduct]
    quantity: strawberry.auto
    results: JSON | None = None
    unit: GraphQLUnit


@strawberry.experimental.pydantic.input(model=LCAxLocation, name="InputLocation")
class GraphQLInputLocation:
    address: strawberry.auto
    city: strawberry.auto
    country: GraphQLCountry


@strawberry.experimental.pydantic.input(model=LCAxValueUnit, name="InputValueUnit")
class GraphQLInputValueUnit:
    unit: GraphQLUnit
    value: strawberry.auto


@strawberry.experimental.pydantic.input(model=LCAxAreaType, name="InputAreaType")
class GraphQLInputAreaType:
    unit: GraphQLUnit
    value: strawberry.auto
    definition: strawberry.auto


@strawberry.experimental.pydantic.input(model=LCAxBuildingModelScope, name="InputBuildingModelScope", all_fields=True)
class GraphQLInputBuildingModelScope:
    pass


@strawberry.experimental.pydantic.input(model=LCAxBuildingInfo, name="InputProjectInfo")
class GraphQLInputBuildingInfo:
    building_completion_year: strawberry.auto
    building_footprint: GraphQLInputValueUnit | None = None
    building_height: GraphQLInputValueUnit | None = None
    building_mass: GraphQLInputValueUnit | None = None
    building_model_scope: GraphQLInputBuildingModelScope | None = None
    building_permit_year: strawberry.auto
    building_type: GraphQLBuildingType | None = None
    building_typology: GraphQLBuildingTypology | None = None
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
    general_energy_class: GraphQLGeneralEnergyClass | None = None
    gross_floor_area: GraphQLInputAreaType
    heated_floor_area: GraphQLInputAreaType
    local_energy_class: strawberry.auto
    roof_type: GraphQLRoofType | None = None


@strawberry.input()
class GraphQLInputProjectInfo:
    building_info: GraphQLInputBuildingInfo | None = None


@strawberry.experimental.pydantic.input(model=LCAxSoftwareInfo, name="InputSoftwareInfo", all_fields=True)
class GraphQLInputSoftwareInfo:
    pass


@strawberry.experimental.pydantic.type(model=LCAxProject, name="InputProject", is_input=True)
class GraphQLInputProject:
    assemblies: list[GraphQLInputAssembly]
    classification_system: strawberry.auto
    comment: strawberry.auto
    description: strawberry.auto
    format_version: strawberry.auto
    id: UUID | None = None
    impact_categories: list[GraphQLImpactCategoryKey]
    lcia_method: strawberry.auto
    life_cycle_stages: list[GraphQLLifeCycleStage]
    location: GraphQLInputLocation
    meta_data: JSON | None = None
    name: strawberry.auto
    owner: strawberry.auto
    project_info: GraphQLInputProjectInfo | None = None
    project_phase: GraphQLProjectPhase
    reference_study_period: strawberry.auto
    results: JSON | None = None
    software_info: GraphQLInputSoftwareInfo


@strawberry.input
class ProjectFilters:
    country: str | None = None
    city: str | None = None
    classification_system: str | None = None
    project_phase: str | None = None


@strawberry.input
class ProjectSortOptions:
    field: str
    order: str  # Should be either 'asc' or 'desc'
