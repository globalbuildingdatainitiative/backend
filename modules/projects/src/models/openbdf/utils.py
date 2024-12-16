from typing import Type


def _resolve_dict_value(klass: dict, key: str, graphql_type: Type):
    if isinstance(klass, dict):
        value = klass.get(key)
    else:
        value = getattr(klass, key, None)

    if value and not callable(value):
        try:
            return graphql_type(**value)
        except TypeError:
            _type = graphql_type()
            _type.__dict__.update(value)
            return _type
