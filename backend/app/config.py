from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(min_length=1)
    database_sslmode: str | None = None
    admin_api_key: str = Field(min_length=8)
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"
    score_stale_after_minutes: int = Field(default=5, gt=0)
    resend_api_key: str | None = None
    email_from: str = Field(min_length=1)
    public_site_url: str = Field(min_length=1)
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

    @property
    def sqlalchemy_database_url(self) -> str:
        database_url = self._normalize_postgres_scheme(self.database_url)
        return self._with_sslmode(database_url)

    @staticmethod
    def _normalize_postgres_scheme(database_url: str) -> str:
        if database_url.startswith("postgres://"):
            return "postgresql+psycopg2://" + database_url.removeprefix(
                "postgres://"
            )

        if database_url.startswith("postgresql://"):
            return "postgresql+psycopg2://" + database_url.removeprefix(
                "postgresql://"
            )

        return database_url

    def _with_sslmode(self, database_url: str) -> str:
        if not self.database_sslmode:
            return database_url

        parsed = urlsplit(database_url)
        if not parsed.scheme.startswith("postgresql"):
            return database_url

        query_params = parse_qsl(parsed.query, keep_blank_values=True)
        if any(key.lower() == "sslmode" for key, _ in query_params):
            return database_url

        query_params.append(("sslmode", self.database_sslmode))
        return urlunsplit(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                urlencode(query_params),
                parsed.fragment,
            )
        )


settings = Settings()
