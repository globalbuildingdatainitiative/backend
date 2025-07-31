from typing import Any, Type, Tuple

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic.fields import FieldInfo
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
)


class ParsingValues(EnvSettingsSource):
    def prepare_field_value(self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool) -> Any:
        if field_name == "BACKEND_CORS_ORIGINS" and value:
            return [x for x in value.split(",")]
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

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_EMAIL: str
    SMTP_NAME: str
    SMTP_PASSWORD: str
    SMTP_USERNAME: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_DB: str = ""
    POSTGRES_PORT: int = 5432
    POSTGRES_URI: PostgresDsn | None = None

    @field_validator("POSTGRES_URI")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> PostgresDsn:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=info.data.get("POSTGRES_USER"),
            password=info.data.get("POSTGRES_PASSWORD"),
            host=info.data.get("POSTGRES_HOST"),
            port=info.data.get("POSTGRES_PORT"),
            path=info.data.get("POSTGRES_DB")
        )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (ParsingValues(settings_cls),)

    class Config:
        case_sensitive = True


settings = Settings()
