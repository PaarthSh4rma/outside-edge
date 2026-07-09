from datetime import date
from html import escape

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.email import EmailBatchRead, EmailPreviewRead
from app.security import require_admin_api_key
from app.services.email_service import (
    EmailConfigurationError,
    EmailIssueNotFoundError,
    EmailService,
)


admin_router = APIRouter(
    prefix="/admin/email",
    tags=["admin"],
    dependencies=[Depends(require_admin_api_key)],
)
public_router = APIRouter(prefix="/unsubscribe", tags=["unsubscribe"])


@admin_router.post("/preview-latest", response_model=EmailPreviewRead)
def preview_latest_email(db: Session = Depends(get_db)):
    try:
        return EmailService().preview_latest(db)
    except EmailIssueNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@admin_router.post("/send-latest", response_model=EmailBatchRead)
def send_latest_email(
    dry_run: bool = Query(default=True),
    force: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    try:
        return EmailService().send_latest(db, dry_run=dry_run, force=force)
    except EmailIssueNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except EmailConfigurationError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@admin_router.post("/send-issue/{issue_date}", response_model=EmailBatchRead)
def send_issue_email(
    issue_date: date,
    dry_run: bool = Query(default=True),
    force: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    try:
        return EmailService().send_issue(
            db,
            issue_date,
            dry_run=dry_run,
            force=force,
        )
    except EmailIssueNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except EmailConfigurationError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@public_router.get("/{token}", response_class=HTMLResponse)
def confirm_unsubscribe(token: str, db: Session = Depends(get_db)):
    subscriber = EmailService().get_unsubscribe_subscriber(db, token)
    if subscriber is None:
        raise HTTPException(status_code=404, detail="Unsubscribe link not found.")

    status_message = (
        "This address is already unsubscribed."
        if not subscriber.is_active
        else "Confirm that you no longer want to receive the Daily Yorker."
    )
    return HTMLResponse(
        _unsubscribe_page(
            title="Unsubscribe from Outside Edge",
            message=status_message,
            form_action=f"/unsubscribe/{escape(token, quote=True)}",
            show_form=subscriber.is_active,
        )
    )


@public_router.post("/{token}", response_class=HTMLResponse)
def unsubscribe(token: str, db: Session = Depends(get_db)):
    subscriber = EmailService().unsubscribe(db, token)
    if subscriber is None:
        raise HTTPException(status_code=404, detail="Unsubscribe link not found.")

    return HTMLResponse(
        _unsubscribe_page(
            title="You're unsubscribed",
            message="You will no longer receive the Daily Yorker.",
            form_action="",
            show_form=False,
        )
    )


def _unsubscribe_page(
    *,
    title: str,
    message: str,
    form_action: str,
    show_form: bool,
) -> str:
    form = ""
    if show_form:
        form = f"""<form method="post" action="{form_action}" style="margin-top:24px;">
  <button type="submit" style="border:0;background:#5fc47d;color:#17211b;padding:12px 18px;font-weight:700;cursor:pointer;">Unsubscribe</button>
</form>"""

    return f"""<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title></head>
  <body style="margin:0;background:#f5f7f5;color:#17211b;font-family:Arial,sans-serif;">
    <main style="max-width:600px;margin:64px auto;padding:0 20px;">
      <p style="color:#3f8f59;font-size:12px;font-weight:700;letter-spacing:2px;text-transform:uppercase;">Outside Edge</p>
      <h1 style="font-size:36px;line-height:1.1;">{escape(title)}</h1>
      <p style="font-size:17px;line-height:1.6;color:#526057;">{escape(message)}</p>
      {form}
    </main>
  </body>
</html>"""
