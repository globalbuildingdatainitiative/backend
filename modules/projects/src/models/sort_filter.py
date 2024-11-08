import re
from typing import Type
from uuid import UUID

import strawberry
from beanie import Document
from beanie.odm.queries.find import FindMany, FindQueryResultType
from strawberry.scalars import JSON
from iso3166 import countries as iso_countries

''' ''
# Implementation 1 (Serverside filter works perfectly)
import re
from typing import Type, Any

import strawberry
from beanie import Document
from beanie.odm.queries.find import FindMany, FindQueryResultType
from strawberry.scalars import JSON
from iso3166 import countries as iso_countries


class BaseFilter:  # pragma: no cover
    def dict(self):
        return self.__dict__

    def keys(self):
        return [key for key, value in self.dict().items() if value]

    def items(self):
        return [(key, value) for key, value in self.dict().items() if value]


def get_matching_country_codes(search_text: str) -> list[str]:
    """Get country codes that match the search text"""
    matching_codes = []
    search_text = search_text.lower()

    for country in iso_countries:
        if search_text in country.name.lower():
            matching_codes.append(country.alpha3.lower())

    return matching_codes


def filter_model_query(
        model: Type[Document], filters: BaseFilter, query: FindMany[FindQueryResultType] | None = None
) -> FindMany[FindQueryResultType]:
    if query is None:
        query = model.find_all(fetch_links=True)

    print(f"Incoming filters: {filters}")  # Debug print

    if filters:
        for _filter, fields in filters.items():
            if not fields:
                continue

            for _field, value in fields.items():
                if not _field or value is None:
                    continue

                print(f"Processing field: {_field} with value: {value}")  # Debug print

                # Handle special case for country field
                if _field in ['countryName', 'project.location.countryName']:
                    field_path = 'project.location.country'
                    if _filter == "contains":
                        matching_codes = get_matching_country_codes(value)
                        if matching_codes:
                            query = query.find({field_path: {"$in": matching_codes}})
                        else:
                            # If no matches found, ensure no results are returned
                            query = query.find({"_id": None})
                    continue

                # Map other field names to database paths
                field_mapping = {
                    'name': 'project.name',
                    'buildingType': 'project.projectInfo.buildingType',
                    'uploadedAt': 'uploadedAt',
                    'public': 'public'
                }

                field_path = field_mapping.get(_field, _field)
                print(f"Mapped field path: {field_path}")  # Debug print

                if _filter == "contains":
                    query = query.find({
                        field_path: {
                            "$regex": f".*{value}.*",
                            "$options": "i"
                        }
                    })
                elif _filter == "equal":
                    query = query.find({
                        field_path: {
                            "$regex": f"^{value}$",
                            "$options": "i"
                        }
                    })
                elif _filter == "is_true" and value is not None:
                    query = query.find({field_path: True})

    return query


def sort_model_query(
        model: Type[Document], sort_by: BaseFilter, query: FindMany[FindQueryResultType] | None = None
) -> FindMany[FindQueryResultType]:
    if query is None:
        query = model.find_all(fetch_links=True)

    if sort_by:
        for sort_direction in ["asc", "dsc"]:
            field = getattr(sort_by, sort_direction)
            if not field:
                continue

            # Special handling for country sort
            if field in ['countryName', 'project.location.countryName']:
                field_path = 'project.location.country'
            else:
                # Convert field path from frontend format to MongoDB format
                field_path = field.replace('project_', 'project.')
                field_path = re.sub(r'([a-z])([A-Z])', r'\1.\2', field_path).lower()

            if sort_direction == "dsc":
                query = query.sort(f"-{field_path}")
            else:
                query = query.sort(f"+{field_path}")

    return query


def to_camel(string: str) -> str:
    return "".join(word.capitalize() for word in string.split("_"))


def to_snake(string: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", string).lower()


@strawberry.input
class FilterBy(BaseFilter):
    equal: JSON | None = None
    contains: JSON | None = None
    starts_with: JSON | None = None
    ends_with: JSON | None = None
    gt: JSON | None = None
    gte: JSON | None = None
    lt: JSON | None = None
    lte: JSON | None = None
    not_equal: JSON | None = None
    is_true: bool | None = None


@strawberry.input(one_of=True)
class SortBy(BaseFilter):
    asc: str | None = strawberry.UNSET
    dsc: str | None = strawberry.UNSET
'''

'''''
# Implementation 2 (Serverside filter works and Sorting works except project name))
import re
from typing import Type, Any

import strawberry
from beanie import Document
from beanie.odm.queries.find import FindMany, FindQueryResultType
from strawberry.scalars import JSON
from iso3166 import countries as iso_countries


class BaseFilter:  # pragma: no cover
    def dict(self):
        return self.__dict__

    def keys(self):
        return [key for key, value in self.dict().items() if value]

    def items(self):
        return [(key, value) for key, value in self.dict().items() if value]


def get_matching_country_codes(search_text: str) -> list[str]:
    """Get country codes that match the search text"""
    matching_codes = []
    search_text = search_text.lower()

    for country in iso_countries:
        if search_text in country.name.lower():
            matching_codes.append(country.alpha3.lower())

    return matching_codes


def filter_model_query(
    model: Type[Document], filters: BaseFilter, query: FindMany[FindQueryResultType] | None = None
) -> FindMany[FindQueryResultType]:
    if query is None:
        query = model.find_all(fetch_links=True)

    print(f"Incoming filters: {filters}")  # Debug print

    if filters:
        for _filter, fields in filters.items():
            if not fields:
                continue

            for _field, value in fields.items():
                if not _field or value is None:
                    continue

                # Handle special case for country field
                if _field in ["countryName", "project.location.countryName"]:
                    field_path = "project.location.country"
                    if _filter == "contains":
                        matching_codes = get_matching_country_codes(value)
                        if matching_codes:
                            query = query.find({field_path: {"$in": matching_codes}})
                        else:
                            # If no matches found, ensure no results are returned
                            query = query.find({"_id": None})
                    continue

                # Map other field names to database paths
                field_mapping = {
                    "name": "project.name", # Not working
                    "buildingType": "project.projectInfo.buildingType",
                    "uploadedAt": "uploadedAt",
                    "public": "public", # Not working
                    "user": "user.firstName", # Not working
                    "lifeCycleStages": "project.lifeCycleStages",
                    "impactCategories": "project.impactCategories",
                }

                field_path = field_mapping.get(_field, _field)

                if _filter == "contains":
                    query = query.find({field_path: {"$regex": f".*{value}.*", "$options": "i"}})
                elif _filter == "equal":
                    query = query.find({field_path: {"$regex": f"^{value}$", "$options": "i"}})
                elif _filter == "is_true" and value is not None:
                    query = query.find({field_path: True})

    return query


def sort_model_query(
    model: Type[Document], sort_by: BaseFilter, query: FindMany[FindQueryResultType] | None = None
) -> FindMany[FindQueryResultType]:
    if query is None:
        query = model.find_all(fetch_links=True)

    if sort_by:
        for sort_direction in ["asc", "dsc"]:
            field = getattr(sort_by, sort_direction)
            if not field:
                continue

            # Map frontend field paths to database paths
            field_mappings = {
                "project.name": "project.name",     # Not working
                "project.location.countryName": "project.location.country",
                "project.projectInfo.buildingType": "project.projectInfo.buildingType",
                "uploadedAt": "uploadedAt",
                "public": "public", # Not working
                "user.firstName": "user.firstName", # Not working
                "project.lifeCycleStages": "project.lifeCycleStages",
                "project.impactCategories": "project.impactCategories",
            }

            # Get the correct field path or use the original if no mapping exists
            field_path = field_mappings.get(field, field)

            # Add sort to existing query
            if sort_direction == "dsc":
                query = query.sort([(field_path, -1)])
            else:
                query = query.sort([(field_path, 1)])

    return query


def to_camel(string: str) -> str:
    return "".join(word.capitalize() for word in string.split("_"))


def to_snake(string: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", string).lower()


@strawberry.input
class FilterBy(BaseFilter):
    equal: JSON | None = None
    contains: JSON | None = None
    starts_with: JSON | None = None
    ends_with: JSON | None = None
    gt: JSON | None = None
    gte: JSON | None = None
    lt: JSON | None = None
    lte: JSON | None = None
    not_equal: JSON | None = None
    is_true: bool | None = None


@strawberry.input(one_of=True)
class SortBy(BaseFilter):
    asc: str | None = strawberry.UNSET
    dsc: str | None = strawberry.UNSET

'''

'''''
# Implementation 3: Tried Strawberry Documentation. Still same error
import re
from typing import Type, Any, Optional

import strawberry
from beanie import Document
from beanie.odm.queries.find import FindMany, FindQueryResultType
from strawberry.scalars import JSON
from iso3166 import countries as iso_countries
from pymongo import ASCENDING, DESCENDING



class BaseFilter:  # pragma: no cover
    asc: Optional[str] = None
    dsc: Optional[str] = None
    def dict(self):
        return self.__dict__

    def keys(self):
        return [key for key, value in self.dict().items() if value]

    def items(self):
        return [(key, value) for key, value in self.dict().items() if value]


def get_matching_country_codes(search_text: str) -> list[str]:
    """Get country codes that match the search text"""
    matching_codes = []
    search_text = search_text.lower()

    for country in iso_countries:
        if search_text in country.name.lower():
            matching_codes.append(country.alpha3.lower())

    return matching_codes


def filter_model_query(
        model: Type[Document], filters: BaseFilter, query: FindMany[FindQueryResultType] | None = None
) -> FindMany[FindQueryResultType]:
    if query is None:
        query = model.find_all(fetch_links=True)

    print(f"Incoming filters: {filters}")  # Debug print

    if filters:
        for _filter, fields in filters.items():
            if not fields:
                continue

            for _field, value in fields.items():
                if not _field or value is None:
                    continue

                print(f"Processing field: {_field} with value: {value}")  # Debug print

                # Handle special case for country field
                if _field in ['countryName', 'project.location.countryName']:
                    field_path = 'project.location.country'
                    if _filter == "contains":
                        matching_codes = get_matching_country_codes(value)
                        if matching_codes:
                            query = query.find({field_path: {"$in": matching_codes}})
                        else:
                            # If no matches found, ensure no results are returned
                            query = query.find({"_id": None})
                    continue

                # Map other field names to database paths
                field_mapping = {
                    'name': 'project.name',
                    'buildingType': 'project.projectInfo.buildingType',
                    'uploadedAt': 'uploadedAt',
                    'public': 'public'
                }

                field_path = field_mapping.get(_field, _field)
                print(f"Mapped field path: {field_path}")  # Debug print

                if _filter == "contains":
                    query = query.find({
                        field_path: {
                            "$regex": f".*{value}.*",
                            "$options": "i"
                        }
                    })
                elif _filter == "equal":
                    query = query.find({
                        field_path: {
                            "$regex": f"^{value}$",
                            "$options": "i"
                        }
                    })
                elif _filter == "is_true" and value is not None:
                    query = query.find({field_path: True})

    return query


def sort_model_query(
    model: Type[Document],
    sort_by: BaseFilter,
    query: FindMany[FindQueryResultType] | None = None
) -> FindMany[FindQueryResultType]:
    if query is None:
        query = model.find_all(fetch_links=True)

    # Check if sort_by has the sort direction specified
    if sort_by:
        sort_fields = []

        # Handle ascending and descending sort keys
        if sort_by.asc:
            # Use "+" syntax and model field references
            field_path = sort_by.asc if not sort_by.asc.startswith("+") else sort_by.asc[1:]
            field = model.__fields__.get(field_path, field_path)
            sort_fields.append((field, ASCENDING))

        if sort_by.dsc:
            # Use "-" syntax and model field references
            field_path = sort_by.dsc if not sort_by.dsc.startswith("-") else sort_by.dsc[1:]
            field = model.__fields__.get(field_path, field_path)
            sort_fields.append((field, DESCENDING))

        # Apply sorted fields to query
        if sort_fields:
            query = query.sort(sort_fields)

    return query


def to_camel(string: str) -> str:
    return "".join(word.capitalize() for word in string.split("_"))


def to_snake(string: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", string).lower()


@strawberry.input
class FilterBy(BaseFilter):
    equal: JSON | None = None
    contains: JSON | None = None
    starts_with: JSON | None = None
    ends_with: JSON | None = None
    gt: JSON | None = None
    gte: JSON | None = None
    lt: JSON | None = None
    lte: JSON | None = None
    not_equal: JSON | None = None
    is_true: bool | None = None


@strawberry.input(one_of=True)
class SortBy(BaseFilter):
    asc: str | None = strawberry.UNSET
    dsc: str | None = strawberry.UNSET

'''


class BaseFilter:  # pragma: no cover
    def dict(self):
        return self.__dict__

    def keys(self):
        return [key for key, value in self.dict().items() if value]

    def items(self):
        return [(key, value) for key, value in self.dict().items() if value]


def get_matching_country_codes(search_text: str) -> list[str]:
    """Get country codes that match the search text"""
    matching_codes = []
    search_text = search_text.lower()

    for country in iso_countries:
        if search_text in country.name.lower():
            matching_codes.append(country.alpha3.lower())

    return matching_codes


def filter_model_query(
    model: Type[Document], filters: BaseFilter, query: FindMany[FindQueryResultType] | None = None
) -> FindMany[FindQueryResultType]:
    if query is None:
        query = model.find_all(fetch_links=True)

    print(f"Incoming filters: {filters}")  # Debug print

    if filters:
        for _filter, fields in filters.items():
            if not fields:
                continue

            for _field, value in fields.items():
                if not _field or value is None:
                    continue

                # Handle special case for country field
                if _field in ["countryName", "project.location.countryName"]:
                    field_path = "project.location.country"
                    if _filter == "contains":
                        matching_codes = get_matching_country_codes(value)
                        if matching_codes:
                            query = query.find({field_path: {"$in": matching_codes}})
                        else:
                            # If no matches found, ensure no results are returned
                            query = query.find({"_id": None})
                    continue

                # Map other field names to database paths
                field_mapping = {
                    "name": "project.name",
                    "buildingType": "project.projectInfo.buildingType",
                    "uploadedAt": "uploadedAt",
                    "public": "public",  # Not working
                    "user": "user.firstName",  # Not working
                    "organization_id": "organization_id",
                    "id": "_id",
                    "_id": "_id",
                    "lifeCycleStages": "project.lifeCycleStages",
                    "impactCategories": "project.impactCategories",
                }

                field_path = field_mapping.get(_field, _field)
                print(f"Mapped field path: {field_path}")  # Debug print

                # Handle UUID fields specially
                if isinstance(value, UUID) or (isinstance(value, str) and len(value) == 36):
                    if _filter == "equal":
                        if isinstance(value, str):
                            try:
                                value = UUID(value)
                            except ValueError:
                                continue
                        query = query.find({field_path: value})
                        print(f"UUID filter query: {field_path} = {value}")  # Debug print
                else:
                    # Handle other field types
                    if _filter == "contains":
                        query = query.find({field_path: {"$regex": f".*{value}.*", "$options": "i"}})
                    elif _filter == "equal":
                        query = query.find({field_path: value})
                    elif _filter == "is_true" and value is not None:
                        query = query.find({field_path: True})

            print(f"Final query: {query.get_filter_query()}")  # Debug the final query
            return query


def sort_model_query(
    model: Type[Document], sort_by: BaseFilter, query: FindMany[FindQueryResultType] | None = None
) -> FindMany[FindQueryResultType]:
    if query is None:
        query = model.find_all(fetch_links=True)

    if sort_by:
        for sort_direction in ["asc", "dsc"]:
            field = getattr(sort_by, sort_direction)
            if not field:
                continue

            # Map frontend field paths to database paths
            field_mappings = {
                "name": "project.name",  # Not working
                "project.location.countryName": "project.location.country",
                "project.projectInfo.buildingType": "project.projectInfo.buildingType",
                "uploadedAt": "uploadedAt",
                "public": "public",  # Not working
                "user.firstName": "user.firstName",  # Not working
                "project.lifeCycleStages": "project.lifeCycleStages",
                "project.impactCategories": "project.impactCategories",
            }

            # Get the correct field path or use the original if no mapping exists
            field_path = field_mappings.get(field, field)

            # Add sort to existing query
            if sort_direction == "dsc":
                query = query.sort([(field_path, -1)])
            else:
                query = query.sort([(field_path, 1)])

    return query


def to_camel(string: str) -> str:
    return "".join(word.capitalize() for word in string.split("_"))


def to_snake(string: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", string).lower()


@strawberry.input
class FilterBy(BaseFilter):
    equal: JSON | None = None
    contains: JSON | None = None
    starts_with: JSON | None = None
    ends_with: JSON | None = None
    gt: JSON | None = None
    gte: JSON | None = None
    lt: JSON | None = None
    lte: JSON | None = None
    not_equal: JSON | None = None
    is_true: bool | None = None


@strawberry.input(one_of=True)
class SortBy(BaseFilter):
    asc: str | None = strawberry.UNSET
    dsc: str | None = strawberry.UNSET
