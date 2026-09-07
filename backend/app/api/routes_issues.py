from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories.issue_repository import IssueRepository
from app.schemas.issue import Issue, IssueRead
from app.security import require_admin_api_key
from app.services.issue_service import IssueGenerationError, IssueService

admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin_api_key)],
)
public_router = APIRouter(prefix="/issues", tags=["issues"])


@admin_router.post("/generate-issue", response_model=IssueRead)
def generate_issue(db: Session = Depends(get_db)):
    issue_service = IssueService()
    try:
        return issue_service.generate_and_save_today_issue(db)
    except IssueGenerationError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@admin_router.post("/preview-issue", response_model=Issue)
def preview_issue():
    issue_service = IssueService()
    try:
        return issue_service.generate_today_issue()
    except IssueGenerationError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@public_router.get("/latest", response_model=IssueRead)
def get_latest_issue(db: Session = Depends(get_db)):
    issue_repository = IssueRepository(db)
    latest_issue = issue_repository.get_latest_issue()

    if not latest_issue:
        raise HTTPException(status_code=404, detail="No issue has been published yet.")

    return issue_repository.to_read_schema(latest_issue)


@public_router.get("", response_model=list[IssueRead])
def get_issue_archive(
    limit: int = Query(default=30, ge=1, le=100),
    db: Session = Depends(get_db),
):
    issue_repository = IssueRepository(db)
    issues = issue_repository.get_published_issues(limit=limit)
    return [issue_repository.to_read_schema(issue) for issue in issues]


@public_router.get("/{issue_date}", response_model=IssueRead)
def get_issue_by_date(issue_date: date, db: Session = Depends(get_db)):
    issue_repository = IssueRepository(db)
    issue = issue_repository.get_published_issue_by_date(issue_date)

    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found.")

    return issue_repository.to_read_schema(issue)
