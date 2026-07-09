from fastapi import FastAPI

from app.api.routes_articles import router as admin_article_router
from app.api.routes_email import admin_router as admin_email_router
from app.api.routes_email import public_router as public_email_router
from app.api.routes_issues import admin_router as admin_issue_router
from app.api.routes_issues import public_router as public_issue_router
from app.api.routes_public_articles import router as public_article_router
from app.api.routes_scores import admin_router as admin_score_router
from app.api.routes_scores import public_router as public_score_router
from app.api.routes_subscribers import admin_router as admin_subscriber_router
from app.api.routes_subscribers import public_router as public_subscriber_router
from app.config import settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Outside Edge API",
    description="Cricket news, caught daily.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(admin_article_router)
app.include_router(admin_issue_router)
app.include_router(public_issue_router)
app.include_router(public_article_router)
app.include_router(public_subscriber_router)
app.include_router(admin_subscriber_router)
app.include_router(public_score_router)
app.include_router(admin_score_router)
app.include_router(admin_email_router)
app.include_router(public_email_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "outside-edge-backend",
    }
