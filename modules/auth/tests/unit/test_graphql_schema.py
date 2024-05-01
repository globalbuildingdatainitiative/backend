from pathlib import Path

from strawberry.cli.utils import load_schema
from strawberry.printer import print_schema


def test_graphql_schema_is_actualized():
    """
    If this test fails it is because the graphql schema hasn't been updated.
    Run export_schema.sh to update the graphql schema
    """
    schema_path = Path(__file__).parent.parent.parent / "graphql" / "schema.graphql"
    graphql_schema = schema_path.read_text()

    generated_schema = print_schema(load_schema("schema", str(Path(__file__).parent.parent.parent / "src")))

    assert graphql_schema.strip() == generated_schema.strip()
