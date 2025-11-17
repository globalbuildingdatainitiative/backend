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

    # # Database Configuration
    # Database Configuration
    # Option 1: Provide full DATABASE_URL directly (takes precedence)
    DATABASE_URL: Optional[str] = Field(
        default=None,
        description="""
            Full database URL. If not set, defaults to SQLite
            or constructed PostgreSQL URL based on other settings: DB_*
            """,
    )

    @computed_field
    def database_url(self) -> str:
        """Get the database URL."""
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL must be set")
        return self.DATABASE_URL

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
