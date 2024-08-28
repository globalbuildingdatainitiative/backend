from enum import Enum
from typing import Type, Iterable

import strawberry
from lcax import BuildingModelScope as LCAxBuildingModelScope
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


def create_enum(name: str, klass: Iterable) -> Type[strawberry.enum]:
    return strawberry.enum(Enum(name, [(_enum.name, _enum.value) for _enum in klass]))


# GraphQLUnit = create_enum("Unit", LCAxUnit
# @strawberry.enum
# class GraphQLUnit(LCAxUnit):
#     pass

GraphQLUnit = strawberry.enum(LCAxUnit)

GraphQLCountry = strawberry.enum(LCAxCountry)
GraphQLStandard = strawberry.enum(LCAxStandard)
GraphQLSubType = strawberry.enum(LCAxSubType)
GraphQLBuildingType = strawberry.enum(LCAxBuildingType)
GraphQLBuildingTypology = strawberry.enum(LCAxBuildingTypology)
GraphQLRoofType = strawberry.enum(LCAxRoofType)
GraphQLGeneralEnergyClass = strawberry.enum(LCAxGeneralEnergyClass)
GraphQLImpactCategoryKey = strawberry.enum(LCAxImpactCategoryKey)
GraphQLProjectPhase = strawberry.enum(LCAxProjectPhase)
GraphQLLifeCycleStage = strawberry.enum(LCAxLifeCycleStage)
GraphQLBuildingModelScope = strawberry.enum(LCAxBuildingModelScope)
