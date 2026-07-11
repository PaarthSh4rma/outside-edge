import sys

from app.db import SessionLocal
from app.jobs.pipeline import generate_today_issue


def main() -> int:
    db = SessionLocal()
    try:
        result = generate_today_issue(db)
        section_text = ", ".join(
            f"{name}={count}"
            for name, count in result.section_counts.items()
        )
        print(
            "generate_issue "
            f"issue_date={result.issue_date} "
            f"issue_id={result.issue_id} "
            f"article_count={result.article_count} "
            f"sections={section_text}"
        )
        return 0
    except Exception as exc:
        print(f"generate_issue failed: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
