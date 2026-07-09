import resend

from app.services.email_providers.base import (
    EmailMessage,
    EmailProvider,
    EmailSendResult,
)


class ResendEmailProvider(EmailProvider):
    name = "resend"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def send(self, message: EmailMessage) -> EmailSendResult:
        resend.api_key = self.api_key
        params: resend.Emails.SendParams = {
            "from": message.from_email,
            "to": [message.to_email],
            "subject": message.subject,
            "html": message.html,
            "text": message.text,
            "headers": message.headers,
        }
        if message.reply_to:
            params["reply_to"] = message.reply_to

        options: resend.Emails.SendOptions | None = None
        if message.idempotency_key:
            options = {"idempotency_key": message.idempotency_key}

        response = resend.Emails.send(params, options)
        return EmailSendResult(provider_message_id=response["id"])
