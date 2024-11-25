from typing import Type


def _resolve_dict_value(klass: dict, key: str, graphql_type: Type):
    value = klass.get("column_grid_long")
    if value:
        return graphql_type(**value)
