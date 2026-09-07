from app.config import Settings


def make_settings(database_url: str, database_sslmode: str | None = None) -> Settings:
    return Settings(
        database_url=database_url,
        database_sslmode=database_sslmode,
        admin_api_key="test-admin-key",
        email_from="Outside Edge <newsletter@example.com>",
        public_site_url="https://outside-edge.test",
    )


def test_settings_normalizes_supabase_postgres_url_for_sqlalchemy():
    settings = make_settings(
        "postgres://user:pass@aws-0-us-east-1.pooler.supabase.com:5432/postgres",
        database_sslmode="require",
    )

    assert settings.sqlalchemy_database_url == (
        "postgresql+psycopg2://user:pass@aws-0-us-east-1.pooler.supabase.com"
        ":5432/postgres?sslmode=require"
    )


def test_settings_preserves_existing_sslmode():
    settings = make_settings(
        "postgresql://user:pass@db.example.supabase.co:5432/postgres"
        "?sslmode=verify-full",
        database_sslmode="require",
    )

    assert settings.sqlalchemy_database_url == (
        "postgresql+psycopg2://user:pass@db.example.supabase.co:5432/postgres"
        "?sslmode=verify-full"
    )
