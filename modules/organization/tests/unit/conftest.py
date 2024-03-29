import pytest
from pytest_alembic.config import Config

from core.connection import create_postgres_engine


@pytest.fixture
def alembic_config():
    """Override this fixture to configure the exact alembic context setup required."""
    yield Config()


@pytest.fixture
def alembic_engine(postgres):
    """Override this fixture to provide pytest-alembic powered tests with a database handle."""
    yield create_postgres_engine()
