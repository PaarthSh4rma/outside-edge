from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.score import MatchRead, ScoreSyncRead
from app.security import require_admin_api_key
from app.services.score_service import ScoreService


public_router = APIRouter(prefix="/matches", tags=["matches"])
admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin_api_key)],
)


@public_router.get("/live", response_model=list[MatchRead])
def get_live_matches(db: Session = Depends(get_db)):
    return ScoreService().get_live_matches(db)


@public_router.get("/upcoming", response_model=list[MatchRead])
def get_upcoming_matches(db: Session = Depends(get_db)):
    return ScoreService().get_upcoming_matches(db)


@public_router.get("/recent", response_model=list[MatchRead])
def get_recent_matches(db: Session = Depends(get_db)):
    return ScoreService().get_recent_matches(db)


@public_router.get("/{match_id}", response_model=MatchRead)
def get_match(match_id: int, db: Session = Depends(get_db)):
    match = ScoreService().get_match(db, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found.")
    return match


@admin_router.post("/sync-scores", response_model=ScoreSyncRead)
def sync_scores(db: Session = Depends(get_db)):
    return ScoreService().sync_scores(db)
