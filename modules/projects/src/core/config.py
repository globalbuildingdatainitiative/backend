from typing import Any, Tuple, Type
import json

from pydantic import AnyHttpUrl, MongoDsn, field_validator
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
            # Check if the value is a JSON array string
            if isinstance(value, str) and value.startswith('[') and value.endswith(']'):
                try:
                    # Parse the JSON array
                    return json.loads(value)
                except json.JSONDecodeError:
                    # If JSON parsing fails, fall back to comma splitting
                    return [x.strip().strip('"\'') for x in value.split(",")]
            else:
                # For non-JSON values, use comma splitting
                return [x.strip().strip('"\'') for x in value.split(",")]
        return super().prepare_field_value(field_name, field, value, value_is_complex)


class Settings(BaseSettings):
    API_STR: str = "/api"
    SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:8000",
    ]
    SUPERTOKENS_CONNECTION_URI: AnyHttpUrl
    SUPERTOKENS_API_KEY: str

    LOG_LEVEL: str = "INFO"

    MONGO_USER: str
    MONGO_PASSWORD: str
    MONGO_HOST: str
    MONGO_DB: str = ""
    MONGO_PORT: int = 27017
    MONGO_URI: MongoDsn | None = None

    @field_validator("MONGO_URI")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> MongoDsn:
        if isinstance(v, str):
            return v
        return MongoDsn.build(
            scheme="mongodb",
            username=info.data.get("MONGO_USER"),
            password=info.data.get("MONGO_PASSWORD"),
            host=info.data.get("MONGO_HOST"),
            port=info.data.get("MONGO_PORT"),
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
