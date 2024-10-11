import json
from pathlib import Path
from typing import Type, Any
from dc_schema import get_schema
from dataclasses_jsonschema import JsonSchemaMixin, SchemaType
from polyfactory.factories import DataclassFactory
from strawberry.types.base import StrawberryList
from pydantic import TypeAdapter
from models import DBProject
from models.openbdf import GraphQLProject
from polyfactory.factories.pydantic_factory import ModelFactory

from models.openbdf.types import GraphQLAssembly
import strawberry.types.arguments
from strawberry.schema.config import StrawberryConfig
from strawberry.schema.types.scalar import DEFAULT_SCALAR_REGISTRY
import schema
from dacite import from_dict

async def serialize_openbdf_schema() -> dict:
    # class ProjectFactory(DataclassFactory[GraphQLProject]):
    #     @classmethod
    #     def get_provider_map(cls) -> dict[Type, Any]:
    #         providers_map = super().get_provider_map()
    #
    #         return {
    #             type(StrawberryList(of_type=GraphQLAssembly)): lambda: StrawberryList(of_type=GraphQLAssembly),
    #             **providers_map,
    #         }
    #
    # dummy_project = ProjectFactory.build()
    project = await DBProject.find_one(fetch_links=True)
    #dummy_project = from_dict(data_class=GraphQLProject, data=project.model_dump())
    #
    # dummy_project = strawberry.types.arguments.convert_argument(project.model_dump(by_alias=True), GraphQLProject, DEFAULT_SCALAR_REGISTRY, schema.schema.config)
    # return dummy_project.to_pydantic().schema_json()
    # return GraphQLProject.json_schema()
    # return JsonSchemaMixin.all_json_schemas(schema_type=SchemaType.DRAFT_06)
    test = GraphQLProject.from_dict(project.model_dump())
    return get_schema(GraphQLProject)