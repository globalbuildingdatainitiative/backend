from typing import Any, Type, Tuple
import json

from pydantic import AnyHttpUrl, Field, computed_field
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
)
from typing import Optional


class ParsingValues(EnvSettingsSource):
    def prepare_field_value(self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool) -> Any:
        if field_name == "BACKEND_CORS_ORIGINS" and value:
            # Check if the value is a JSON array string
            if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
                try:
                    # Parse the JSON array
                    return json.loads(value)
                except json.JSONDecodeError:
                    # If JSON parsing fails, fall back to comma splitting
                    return [x.strip().strip("\"'") for x in value.split(",")]
            else:
                # For non-JSON values, use comma splitting
                return [x.strip().strip("\"'") for x in value.split(",")]
        return super().prepare_field_value(field_name, field, value, value_is_complex)


class Settings(BaseSettings):
    API_STR: str = "/api"
    SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl
    ROUTER_URL: AnyHttpUrl
    CONNECTION_URI: AnyHttpUrl
    API_KEY: str
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:8000",
        "http://localhost:7000",
    ]
    LOG_LEVEL: str = "INFO"
    SUPERTOKENS_TENANT_ID: str = "public"

    # # Database configuration necessary for tests only
    # TEST_DB_USER: str = "test_user"
    # TEST_DB_PASSWORD: str = "test_password"
    # TEST_DB_NAME: str = "test_db"
    # TEST_DB_PORT: int = 5432

    # # Database Configuration
    # POSTGRESQL_CONNECTION_URI: str | None = None
    # POSTGRESQL_CONNECTION_URI_LOCAL: str | None = None

    # Database Configuration
    # Option 1: Provide full DATABASE_URL directly (takes precedence)
    DATABASE_URL: Optional[str] = Field(
        default=None,
        description="""
            Full database URL. If not set, defaults to SQLite
            or constructed PostgreSQL URL based on other settings: DB_*
            """,
    )

    # Option 2: Provide PostgreSQL connection details (optional, for PostgreSQL)
    DB_USER: Optional[str] = Field(default=None, description="Database user (optional, for PostgreSQL)")
    DB_PASSWORD: Optional[str] = Field(default=None, description="Database password (optional, for PostgreSQL)")
    DB_NAME: Optional[str] = Field(default=None, description="Database name (optional, for PostgreSQL)")

    # necessary to build the DB URL if DATABASE_URL is not provided
    DB_HOST: Optional[str] = Field(default=None, description="Database host (optional, for PostgreSQL)")
    DB_HOST_PORT: int = Field(default=5432, description="Database port (optional, for PostgreSQL)")

    @computed_field
    def database_url(self) -> str:
        """
        Get the database URL.

        Priority:
        1. If DATABASE_URL is explicitly set, use it
        2. If DB_USER, DB_PASSWORD, DB_HOST, DB_NAME are all set, build PostgreSQL URL
        3. Otherwise, default to SQLite
        """
        # If DATABASE_URL is explicitly provided, use it
        if self.DATABASE_URL:
            return self.DATABASE_URL

        # If PostgreSQL credentials are provided, build the URL
        if all([self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_NAME]):
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_HOST_PORT}/{self.DB_NAME}"

        # Default to SQLite for local development
        return "sqlite+aiosqlite:///./co2_calculator.db"

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_EMAIL: str
    SMTP_NAME: str
    SMTP_PASSWORD: str = ""
    SMTP_USERNAME: str = ""

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (dotenv_settings, ParsingValues(settings_cls))

    # @property
    # def database_url(self) -> str | None:
    #     """Get the appropriate database URL, preferring LOCAL for development"""
    #     return self.POSTGRESQL_CONNECTION_URI_LOCAL or self.POSTGRESQL_CONNECTION_URI

    model_config = SettingsConfigDict(case_sensitive=True)


class _SettingsProxy:
    """Proxy that delays Settings() until first access."""

    _instance: Settings | None = None

    def __getattr__(self, name: str):
        if self._instance is None:
            self._instance = Settings()
        return getattr(self._instance, name)


# Use everywhere instead of Settings()
settings = _SettingsProxy()
