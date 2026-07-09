from app.services.email_providers.base import EmailProvider
from app.services.email_providers.resend_provider import ResendEmailProvider


def get_email_provider(api_key: str) -> EmailProvider:
    return ResendEmailProvider(api_key)
