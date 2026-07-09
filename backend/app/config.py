from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    admin_api_key: str
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"
    score_stale_after_minutes: int = Field(default=5, gt=0)
    resend_api_key: str | None = None
    email_from: str
    public_site_url: str
    email_reply_to: str | None = None
    email_dry_run: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def allowed_cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()
