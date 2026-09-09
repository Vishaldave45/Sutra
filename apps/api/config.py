from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Sutra API"
    environment: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"
    database_url: str = (
        "postgresql+psycopg://sutra_user:sutra_password@localhost:5444/sutra_db"
    )

    @property
    def database_url_sync(self) -> str:
        """Synchronous connection URL used by Alembic migrations with psycopg 3."""
        if self.database_url.startswith("postgresql+psycopg://"):
            return self.database_url
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace(
                "postgresql://", "postgresql+psycopg://", 1
            )
        return self.database_url

    model_config = SettingsConfigDict(
        env_prefix="SUTRA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
