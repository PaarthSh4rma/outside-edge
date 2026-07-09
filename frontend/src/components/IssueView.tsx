import type { Issue } from "../types/issue";
import type { ThemeMode } from "../types/theme";
import { formatDate } from "../utils/date";

export function IssueView({
  issue,
  themeMode,
  compact = false,
}: {
  issue: Issue;
  themeMode: ThemeMode;
  compact?: boolean;
}) {
  return (
    <article>
      <header
        className={`border-b pb-6 ${
          themeMode === "dark" ? "border-white/10" : "border-black/10"
        }`}
      >
        <p className="text-xs font-black uppercase tracking-[0.2em] text-[#5fc47d]">
          {formatDate(issue.issue_date)}
        </p>
        <h1
          className={`mt-3 font-black tracking-normal ${
            compact
              ? "text-3xl sm:text-4xl"
              : "text-4xl sm:text-5xl md:text-6xl"
          }`}
        >
          {issue.title}
        </h1>
        <p
          className={`mt-3 text-base ${
            themeMode === "dark" ? "text-white/60" : "text-black/60"
          }`}
        >
          {issue.tagline}
        </p>
      </header>

      <div className="mt-8 space-y-10">
        {issue.sections.map((section) => (
          <section key={section.name}>
            <div className="mb-4">
              <h2 className="text-xl font-black sm:text-2xl">{section.name}</h2>
              <p
                className={`mt-1 text-sm ${
                  themeMode === "dark" ? "text-white/55" : "text-black/55"
                }`}
              >
                {section.description}
              </p>
            </div>
            <div
              className={`divide-y ${
                themeMode === "dark" ? "divide-white/10" : "divide-black/10"
              }`}
            >
              {section.articles.map((article, index) => (
                <a
                  key={article.id}
                  href={article.url}
                  target="_blank"
                  rel="noreferrer"
                  className="group grid grid-cols-[2rem_1fr] gap-3 py-5 first:pt-0"
                >
                  <span className="pt-1 text-xs font-black text-[#5fc47d]">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                  <span className="min-w-0">
                    <span className="mb-2 flex flex-wrap gap-x-2 text-xs font-bold uppercase text-current opacity-50">
                      <span>{article.source}</span>
                      {article.published_at && (
                        <span>{formatDate(article.published_at)}</span>
                      )}
                    </span>
                    <span className="block text-lg font-black leading-snug group-hover:text-[#5fc47d] sm:text-xl">
                      {article.title}
                    </span>
                    {article.summary && (
                      <span className="mt-2 line-clamp-3 block text-sm leading-6 opacity-60">
                        {stripHtml(article.summary)}
                      </span>
                    )}
                  </span>
                </a>
              ))}
            </div>
          </section>
        ))}
      </div>
    </article>
  );
}

function stripHtml(value: string) {
  return value.replace(/<[^>]*>/g, "");
}
