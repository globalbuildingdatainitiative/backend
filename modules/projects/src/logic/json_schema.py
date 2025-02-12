import dataclasses
import datetime
import enum
import numbers
import typing as t
import uuid
from types import UnionType

from strawberry.annotation import StrawberryAnnotation
from strawberry.types.base import StrawberryList, StrawberryOptional
from strawberry.types.enum import EnumDefinition
from strawberry.types.scalar import ScalarWrapper
from strawberry.types.union import StrawberryUnion

_MISSING = dataclasses.MISSING


def get_schema(dc):
    return _GetSchema()(dc)


_Format = t.Literal[
    "date-time",
    "time",
    "date",
    "duration",
    "email",
    "idn-email",
    "hostname",
    "idn-hostname",
    "ipv4",
    "ipv6",
    "uuid",
    "uri",
    "uri-reference",
    "iri",
    "iri-reference",
]


@dataclasses.dataclass(frozen=True)
class SchemaAnnotation:
    title: t.Optional[str] = None
    description: t.Optional[str] = None
    examples: t.Optional[list[t.Any]] = None
    deprecated: t.Optional[bool] = None
    min_length: t.Optional[int] = None
    max_length: t.Optional[int] = None
    pattern: t.Optional[str] = None
    format: t.Optional[_Format] = None
    minimum: t.Optional[numbers.Number] = None
    maximum: t.Optional[numbers.Number] = None
    exclusive_minimum: t.Optional[numbers.Number] = None
    exclusive_maximum: t.Optional[numbers.Number] = None
    multiple_of: t.Optional[numbers.Number] = None
    min_items: t.Optional[int] = None
    max_items: t.Optional[int] = None
    unique_items: t.Optional[bool] = None

    def schema(self):
        key_map = {
            "min_length": "minLength",
            "max_length": "maxLength",
            "exclusive_minimum": "exclusiveMinimum",
            "exclusive_maximum": "exclusiveMaximum",
            "multiple_of": "multipleOf",
            "min_items": "minItems",
            "max_items": "maxItems",
            "unique_items": "uniqueItems",
        }
        return {key_map.get(k, k): v for k, v in dataclasses.asdict(self).items() if v is not None}


class _GetSchema:
    def __call__(self, dc):
        self.root = dc
        self.seen_root = False

        self.defs = {}
        schema = self.get_dc_schema(dc, SchemaAnnotation())
        if self.defs:
            schema["$defs"] = self.defs

        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            **schema,
        }

    def get_dc_schema(self, dc, annotation):
        if dc == self.root:
            if self.seen_root:
                return {"allOf": [{"$ref": "#"}], **annotation.schema()}
            else:
                self.seen_root = True
                schema = self.create_dc_schema(dc)
                return schema
        else:
            if self._get_name(dc) not in self.defs:
                schema = self.create_dc_schema(dc)
                self.defs[self._get_name(dc)] = schema
            return {
                "allOf": [{"$ref": f"#/$defs/{self._get_name(dc)}"}],
                **annotation.schema(),
            }

    def create_dc_schema(self, dc):
        if hasattr(dc, "SchemaConfig"):
            annotation = getattr(dc.SchemaConfig, "annotation", SchemaAnnotation())
        else:
            annotation = SchemaAnnotation()
        schema = {
            "type": "object",
            "title": self._get_name(dc),
            **annotation.schema(),
            "properties": {},
            "required": [],
        }
        type_hints = t.get_type_hints(dc, include_extras=True)
        for field in dataclasses.fields(dc):
            type_ = type_hints[field.name]
            if isinstance(type_, EnumDefinition):
                type_ = type_.wrapped_cls

            # if isinstance(type_, StrawberryOptional):
            #     type_ = type_.of_type
            elif isinstance(type_, StrawberryAnnotation):
                type_ = type_.raw_annotation
            _property = self.get_field_schema(
                type_ if not isinstance(type_, ScalarWrapper) else type_.wrap, field.default, SchemaAnnotation()
            )
            if _property is None:
                continue
            schema["properties"][self.get_field_name(field)] = _property
            field_is_optional = self.is_field_optional(field, type_hints[field.name])
            if not field_is_optional:
                schema["required"].append(self.get_field_name(field))
        if not schema["required"]:
            schema.pop("required")
        return schema

    @staticmethod
    def get_field_name(field):
        if hasattr(field, "graphql_name") and field.graphql_name is not None:
            return field.graphql_name
        else:
            return field.name

    @staticmethod
    def is_field_optional(field, origin_type):
        if isinstance(origin_type, StrawberryOptional):
            return True
        return field.default is not _MISSING or field.default_factory is not _MISSING

    def get_field_schema(self, type_, default, annotation):
        if isinstance(type_, EnumDefinition):
            type_ = type_.wrapped_cls
        if dataclasses.is_dataclass(type_):
            return self.get_dc_schema(type_, annotation)
        if t.get_origin(type_) in [t.Union, UnionType] or isinstance(type_, StrawberryOptional):
            return self.get_union_schema(type_, default, annotation)
        if t.get_origin(type_) == t.Literal:
            return self.get_literal_schema(type_, default, annotation)
        if t.get_origin(type_) == t.Annotated:
            return self.get_annotated_schema(type_, default)
        elif type_ is dict or t.get_origin(type_) is dict:
            return self.get_dict_schema(type_, annotation)
        elif isinstance(type_, StrawberryList):
            return self.get_list_schema(type_, annotation)
        elif isinstance(type_, StrawberryUnion):
            return self.get_union_schema(type_, default, annotation)
        elif type_ is list or t.get_origin(type_) is list:
            return self.get_list_schema(type_, annotation)
        elif type_ is tuple or t.get_origin(type_) is tuple:
            return self.get_tuple_schema(type_, default, annotation)
        elif type_ is set or t.get_origin(type_) is set:
            return self.get_set_schema(type_, annotation)
        elif type_ is None or type_ is type(None):
            return self.get_none_schema(default, annotation)
        elif type_ is str:
            return self.get_str_schema(default, annotation)
        elif type_ is bool:
            return self.get_bool_schema(default, annotation)
        elif type_ is int:
            return self.get_int_schema(default, annotation)
        elif type_.__name__ == "Base64" or type_.__name__ == "JSON":
            return self.get_str_schema(default, annotation)
        elif issubclass(type_, numbers.Number):
            return self.get_number_schema(default, annotation)
        elif issubclass(type_, enum.Enum):
            return self.get_enum_schema(type_, default, annotation)
        elif issubclass(type_, datetime.datetime):
            return self.get_datetime_schema(annotation)
        elif issubclass(type_, datetime.date):
            return self.get_date_schema(annotation)
        elif issubclass(type_, uuid.UUID):
            return self.get_uuid_schema()
        else:
            raise NotImplementedError(f"field type '{type_}' not implemented")

    @staticmethod
    def _get_name(dc):
        if hasattr(dc, "__strawberry_definition__"):
            return dc.__strawberry_definition__.name
        elif hasattr(dc, "__name__"):
            return dc.__name__
        else:
            return dc.name

    def get_union_schema(self, type_, default, annotation):
        if isinstance(type_, StrawberryOptional):
            args = (type(None), type_.of_type)
        else:
            args = t.get_args(type_) or type_.types
        if default is _MISSING:
            return {
                "anyOf": [
                    self.get_field_schema(
                        arg if not isinstance(arg, ScalarWrapper) else arg.wrap, _MISSING, SchemaAnnotation()
                    )
                    for arg in args
                ],
                **annotation.schema(),
            }
        else:
            return {
                "anyOf": [
                    self.get_field_schema(
                        arg if not isinstance(arg, ScalarWrapper) else arg.wrap, _MISSING, SchemaAnnotation()
                    )
                    for arg in args
                ],
                "default": default,
                **annotation.schema(),
            }

    def get_literal_schema(self, type_, default, annotation):
        if default is _MISSING:
            schema = {**annotation.schema()}
        else:
            schema = {"default": default, **annotation.schema()}
        args = t.get_args(type_)
        return {"enum": list(args), **schema}

    def get_dict_schema(self, type_, annotation):
        args = t.get_args(type_)
        assert len(args) in (0, 2)
        if args:
            assert args[0] is str
            return {
                "type": "object",
                "additionalProperties": self.get_field_schema(args[1], _MISSING, SchemaAnnotation()),
                **annotation.schema(),
            }
        else:
            return {"type": "object", **annotation.schema()}

    def get_list_schema(self, type_, annotation):
        args = t.get_args(type_)
        assert len(args) in (0, 1)
        if args:
            return {
                "type": "array",
                "items": self.get_field_schema(args[0], _MISSING, SchemaAnnotation()),
                **annotation.schema(),
            }
        elif isinstance(type_, StrawberryList):
            return {
                "type": "array",
                "items": self.get_field_schema(type_.of_type, _MISSING, SchemaAnnotation()),
                **annotation.schema(),
            }
        else:
            return {"type": "array", **annotation.schema()}

    def get_tuple_schema(self, type_, default, annotation):
        if default is _MISSING:
            schema = {**annotation.schema()}
        else:
            schema = {"default": list(default), **annotation.schema()}
        args = t.get_args(type_)
        if args and len(args) == 2 and args[1] is ...:
            schema = {
                "type": "array",
                "items": self.get_field_schema(args[0], _MISSING, SchemaAnnotation()),
                **schema,
            }
        elif args:
            schema = {
                "type": "array",
                "prefixItems": [self.get_field_schema(arg, _MISSING, SchemaAnnotation()) for arg in args],
                "minItems": len(args),
                "maxItems": len(args),
                **schema,
            }
        else:
            schema = {"type": "array", **schema}
        return schema

    def get_set_schema(self, type_, annotation):
        args = t.get_args(type_)
        assert len(args) in (0, 1)
        if args:
            return {
                "type": "array",
                "items": self.get_field_schema(args[0], _MISSING, SchemaAnnotation()),
                "uniqueItems": True,
                **annotation.schema(),
            }
        else:
            return {"type": "array", "uniqueItems": True, **annotation.schema()}

    def get_none_schema(self, default, annotation):
        if default is _MISSING:
            return {"type": "null", **annotation.schema()}
        else:
            return {"type": "null", "default": default, **annotation.schema()}

    def get_str_schema(self, default, annotation):
        if default is _MISSING:
            return {"type": "string", **annotation.schema()}
        else:
            try:
                return {"type": "string", "default": default, **annotation.schema()}
            except AttributeError:
                return None

    def get_bool_schema(self, default, annotation):
        if default is _MISSING:
            return {"type": "boolean", **annotation.schema()}
        else:
            return {"type": "boolean", "default": default, **annotation.schema()}

    def get_int_schema(self, default, annotation):
        if default is _MISSING:
            return {"type": "integer", **annotation.schema()}
        else:
            return {"type": "integer", "default": default, **annotation.schema()}

    def get_number_schema(self, default, annotation):
        if default is _MISSING:
            return {"type": "number", **annotation.schema()}
        else:
            return {"type": "number", "default": default, **annotation.schema()}

    def get_enum_schema(self, type_, default, annotation):
        if type_.__name__ not in self.defs:
            self.defs[type_.__name__] = {
                "title": type_.__name__,
                "enum": [v.value for v in type_],
            }
        if default is _MISSING:
            return {
                "allOf": [{"$ref": f"#/$defs/{type_.__name__}"}],
                **annotation.schema(),
            }
        else:
            return {
                "allOf": [{"$ref": f"#/$defs/{type_.__name__}"}],
                "default": default.value,
                **annotation.schema(),
            }

    def get_annotated_schema(self, type_, default):
        args = t.get_args(type_)
        assert len(args) == 2
        return self.get_field_schema(args[0], default, args[1])

    def get_datetime_schema(self, annotation):
        return {"type": "string", "format": "date-time", **annotation.schema()}

    def get_date_schema(self, annotation):
        return {"type": "string", "format": "date", **annotation.schema()}

    def get_uuid_schema(self):
        return {
            "type": "string",
            "format": "uuid",
            "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        }
