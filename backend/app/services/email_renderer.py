from datetime import date
from html import escape

from app.schemas.issue import IssueRead
from app.schemas.email import RenderedEmail


class DailyYorkerEmailRenderer:
    def render(
        self,
        issue: IssueRead,
        public_site_url: str,
        unsubscribe_url: str,
    ) -> RenderedEmail:
        site_url = public_site_url.rstrip("/")
        web_issue_url = f"{site_url}/daily-yorker/{issue.issue_date.isoformat()}"
        subject = f"The Daily Yorker | {self._format_date(issue.issue_date)}"

        return RenderedEmail(
            subject=subject,
            html=self._render_html(issue, web_issue_url, unsubscribe_url),
            text=self._render_text(issue, web_issue_url, unsubscribe_url),
            issue_date=issue.issue_date,
            web_issue_url=web_issue_url,
        )

    def _render_html(
        self,
        issue: IssueRead,
        web_issue_url: str,
        unsubscribe_url: str,
    ) -> str:
        sections = "".join(
            self._render_html_section(section.name, section.description, section.articles)
            for section in issue.sections
        )
        return f"""<!doctype html>
<html lang="en">
  <body style="margin:0;background:#f5f7f5;color:#17211b;font-family:Arial,sans-serif;">
    <div style="display:none;max-height:0;overflow:hidden;">{escape(issue.tagline)}</div>
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f5f7f5;">
      <tr><td align="center" style="padding:24px 12px;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:680px;background:#ffffff;border:1px solid #dfe5e1;">
          <tr><td style="padding:24px 28px;background:#101513;color:#ffffff;">
            <p style="margin:0;color:#d7ff3f;font-size:12px;font-weight:700;letter-spacing:2px;text-transform:uppercase;">Outside Edge</p>
            <h1 style="margin:10px 0 0;font-size:32px;line-height:1.1;">The Daily Yorker</h1>
            <p style="margin:10px 0 0;color:#b9c3bd;font-size:15px;">{escape(self._format_date(issue.issue_date))} · {escape(issue.tagline)}</p>
          </td></tr>
          <tr><td style="padding:8px 28px 28px;">
            {sections}
            <p style="margin:28px 0 0;">
              <a href="{escape(web_issue_url, quote=True)}" style="display:inline-block;background:#5fc47d;color:#17211b;padding:12px 18px;text-decoration:none;font-weight:700;">Read this issue on Outside Edge</a>
            </p>
          </td></tr>
          <tr><td style="padding:22px 28px;background:#eef2ef;color:#526057;font-size:12px;line-height:1.6;">
            <strong style="color:#17211b;">Outside Edge</strong><br>
            Ad-free cricket intelligence and the Daily Yorker briefing.<br>
            You received this because you subscribed to Outside Edge.
            <a href="{escape(unsubscribe_url, quote=True)}" style="color:#365f44;">Unsubscribe</a>
          </td></tr>
        </table>
      </td></tr>
    </table>
  </body>
</html>"""

    def _render_html_section(self, name: str, description: str, articles) -> str:
        article_rows = "".join(
            f"""<li style="margin:0 0 18px;">
  <a href="{escape(str(article.url), quote=True)}" style="color:#17211b;font-size:17px;font-weight:700;line-height:1.35;text-decoration:none;">{escape(article.title)}</a>
  <p style="margin:5px 0 0;color:#637067;font-size:12px;text-transform:uppercase;">{escape(article.source)}</p>
</li>"""
            for article in articles
        )
        return f"""<section style="padding-top:24px;">
  <h2 style="margin:0;font-size:22px;">{escape(name)}</h2>
  <p style="margin:6px 0 16px;color:#637067;font-size:14px;">{escape(description)}</p>
  <ol style="margin:0;padding-left:22px;">{article_rows}</ol>
</section>"""

    def _render_text(
        self,
        issue: IssueRead,
        web_issue_url: str,
        unsubscribe_url: str,
    ) -> str:
        lines = [
            "OUTSIDE EDGE",
            "THE DAILY YORKER",
            self._format_date(issue.issue_date),
            issue.tagline,
            "",
        ]
        for section in issue.sections:
            lines.extend([section.name.upper(), section.description])
            for index, article in enumerate(section.articles, start=1):
                lines.extend(
                    [
                        f"{index}. {article.title}",
                        f"Source: {article.source}",
                        str(article.url),
                        "",
                    ]
                )

        lines.extend(
            [
                f"Read this issue on Outside Edge: {web_issue_url}",
                "",
                "Outside Edge - ad-free cricket intelligence.",
                f"Unsubscribe: {unsubscribe_url}",
            ]
        )
        return "\n".join(lines)

    def _format_date(self, value: date) -> str:
        return value.strftime("%-d %B %Y")
