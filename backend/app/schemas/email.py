from datetime import date

from pydantic import BaseModel


class RenderedEmail(BaseModel):
    subject: str
    html: str
    text: str
    issue_date: date
    web_issue_url: str


class EmailPreviewRead(BaseModel):
    subject: str
    html_preview: str
    text_preview: str
    issue_date: date
    would_send_count: int
    skipped_count: int
    dry_run: bool


class EmailBatchRead(EmailPreviewRead):
    sent_count: int
    failed_count: int
