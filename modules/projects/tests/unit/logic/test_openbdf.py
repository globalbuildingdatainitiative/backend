import jsonschema
import pytest
from jsonschema import Draft202012Validator

from logic import serialize_openbdf_schema


@pytest.mark.asyncio
async def test_serialize_openbdf_schema():
    schema = await serialize_openbdf_schema()

    assert schema
    Draft202012Validator.check_schema(schema)
