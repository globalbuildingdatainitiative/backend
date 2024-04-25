from pydantic import AnyHttpUrl, MongoDsn, field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_STR: str = "/api"
    SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:8000",
    ]
    SUPERTOKENS_CONNECTION_URI: AnyHttpUrl
    SUPERTOKENS_API_KEY: str

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

    @field_validator("BACKEND_CORS_ORIGINS")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True


settings = Settings()
