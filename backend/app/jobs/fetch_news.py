import sys

from app.db import SessionLocal
from app.jobs.pipeline import fetch_news


def main() -> int:
    db = SessionLocal()
    try:
        result = fetch_news(db)
        print(
            "fetch_news "
            f"fetched_count={result.fetched_count} "
            f"saved_count={result.saved_count}"
        )
        return 0
    except Exception as exc:
        print(f"fetch_news failed: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
