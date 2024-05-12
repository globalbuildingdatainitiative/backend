from enum import Enum
from typing import Type

import strawberry
from lcax import BuildingType as LCAxBuildingType
from lcax import BuildingTypology as LCAxBuildingTypology
from lcax import Country as LCAxCountry
from lcax import GeneralEnergyClass as LCAxGeneralEnergyClass
from lcax import ImpactCategoryKey as LCAxImpactCategoryKey
from lcax import LifeCycleStage as LCAxLifeCycleStage
from lcax import ProjectPhase as LCAxProjectPhase
from lcax import RoofType as LCAxRoofType
from lcax import Standard as LCAxStandard
from lcax import SubType as LCAxSubType
from lcax import Unit as LCAxUnit

GraphQLUnit = strawberry.enum(Enum("Unit", [_enum.value for _enum in LCAxUnit]))
GraphQLCountry: Type[Enum] = strawberry.enum(Enum("Country", [_enum.value for _enum in LCAxCountry]))
GraphQLStandard = strawberry.enum(Enum("Standard", [_enum.value for _enum in LCAxStandard]))
GraphQLSubType = strawberry.enum(Enum("SubType", [_enum.value for _enum in LCAxSubType]))
GraphQLBuildingType = strawberry.enum(Enum("BuildingType", [_enum.value for _enum in LCAxBuildingType]))
GraphQLBuildingTypology = strawberry.enum(Enum("BuildingTypology", [_enum.value for _enum in LCAxBuildingTypology]))
GraphQLRoofType = strawberry.enum(Enum("RoofType", [_enum.value for _enum in LCAxRoofType]))
GraphQLGeneralEnergyClass = strawberry.enum(
    Enum("GeneralEnergyClass", [_enum.value for _enum in LCAxGeneralEnergyClass])
)
GraphQLImpactCategoryKey = strawberry.enum(Enum("ImpactCategoryKey", [_enum.value for _enum in LCAxImpactCategoryKey]))
GraphQLProjectPhase = strawberry.enum(Enum("ProjectPhase", [_enum.value for _enum in LCAxProjectPhase]))
GraphQLLifeCycleStage = strawberry.enum(Enum("LifeCycleStage", [_enum.value for _enum in LCAxLifeCycleStage]))
