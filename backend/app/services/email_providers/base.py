from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True)
class EmailMessage:
    to_email: str
    from_email: str
    reply_to: str | None
    subject: str
    html: str
    text: str
    headers: dict[str, str] = field(default_factory=dict)
    idempotency_key: str | None = None


@dataclass(frozen=True)
class EmailSendResult:
    provider_message_id: str


class EmailProvider(ABC):
    name: str

    @abstractmethod
    def send(self, message: EmailMessage) -> EmailSendResult:
        pass
