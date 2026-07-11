import argparse
import sys

from app.db import SessionLocal
from app.jobs.pipeline import publish_daily_yorker


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch news, generate today's Daily Yorker, and email it safely.",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Render and count recipients without sending real email.",
    )
    mode.add_argument(
        "--send",
        action="store_true",
        help="Attempt delivery, still respecting EMAIL_DRY_RUN safety lock.",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        result = publish_daily_yorker(db, dry_run=args.dry_run)
        section_text = ", ".join(
            f"{name}={count}"
            for name, count in result.section_counts.items()
        )
        print(
            "publish_daily_yorker "
            f"mode={'dry-run' if args.dry_run else 'send'} "
            f"effective_dry_run={str(result.dry_run).lower()} "
            f"fetched_count={result.fetched_count} "
            f"saved_count={result.saved_count} "
            f"issue_date={result.issue_date} "
            f"issue_id={result.issue_id} "
            f"article_count={result.article_count} "
            f"sections={section_text} "
            f"would_send_count={result.would_send_count} "
            f"sent_count={result.sent_count} "
            f"skipped_count={result.skipped_count} "
            f"failed_count={result.failed_count}"
        )
        return 0
    except Exception as exc:
        print(f"publish_daily_yorker failed: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
