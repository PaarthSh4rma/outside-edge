from datetime import date

from app.schemas.article import ArticleRead
from app.schemas.issue import IssueRead, IssueSectionRead
from app.services.email_renderer import DailyYorkerEmailRenderer


def test_daily_yorker_renderer_includes_identity_sections_and_links():
    article = ArticleRead(
        id=1,
        title="Australia names Test squad",
        url="https://example.com/test-squad",
        source="Test Cricket Desk",
        published_at=None,
        summary="Squad news.",
        category="world_cricket",
    )
    issue = IssueRead(
        id=1,
        issue_date=date(2026, 7, 9),
        title="The Daily Yorker",
        tagline="Cricket news, caught daily.",
        status="published",
        sections=[
            IssueSectionRead(
                name=name,
                description=f"{name} stories.",
                articles=[article],
            )
            for name in ["Opening Spell", "Powerplay", "Around the Grounds"]
        ],
    )

    rendered = DailyYorkerEmailRenderer().render(
        issue,
        "https://outside-edge.test",
        "https://outside-edge.test/unsubscribe/raw-token",
    )

    assert rendered.subject == "The Daily Yorker | 9 July 2026"
    assert "Outside Edge" in rendered.html
    assert "Opening Spell" in rendered.html
    assert "Powerplay" in rendered.html
    assert "Around the Grounds" in rendered.html
    assert "https://example.com/test-squad" in rendered.html
    assert "daily-yorker/2026-07-09" in rendered.html
    assert "unsubscribe/raw-token" in rendered.html
    assert "OUTSIDE EDGE" in rendered.text
    assert "Source: Test Cricket Desk" in rendered.text
