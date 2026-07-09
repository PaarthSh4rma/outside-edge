import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { apiGet } from "../api/client";
import type { Issue } from "../types/issue";
import type { ThemeMode } from "../types/theme";
import { formatDate } from "../utils/date";

export function ArchivePage({ themeMode }: { themeMode: ThemeMode }) {
  const [issues, setIssues] = useState<Issue[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    apiGet<Issue[]>("/issues")
      .then(setIssues)
      .catch(() =>
        setErrorMessage(
          "Outside Edge could not reach the archive service. Please try again shortly.",
        ),
      )
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <section className="py-8 sm:py-12">
      <header className="max-w-3xl">
        <p className="text-xs font-black uppercase tracking-[0.2em] text-[#5fc47d]">
          Daily archive
        </p>
        <h1 className="mt-4 text-4xl font-black tracking-normal sm:text-6xl">
          The Daily Yorker
        </h1>
        <p className="mt-5 text-base leading-7 opacity-60 sm:text-lg">
          Every Outside Edge briefing, filed by date and built for a focused
          five-minute read.
        </p>
      </header>

      <div
        className={`mt-10 border-t ${
          themeMode === "dark" ? "border-white/10" : "border-black/10"
        }`}
      >
        {isLoading && <p className="py-8 text-sm opacity-55">Loading archive...</p>}
        {errorMessage && (
          <div className="max-w-xl py-8">
            <h2 className="text-xl font-black">The archive is off the field.</h2>
            <p className="mt-2 text-sm leading-6 opacity-55">{errorMessage}</p>
          </div>
        )}
        {!isLoading && !errorMessage && issues.length === 0 && (
          <div className="max-w-xl py-8">
            <h2 className="text-xl font-black">The archive is ready for its first issue.</h2>
            <p className="mt-2 text-sm leading-6 opacity-55">
              No Daily Yorker issues yet. Once the first briefing is published,
              it will appear here by date.
            </p>
          </div>
        )}
        {issues.map((issue) => (
          <Link
            key={issue.id}
            to={`/daily-yorker/${issue.issue_date}`}
            className={`group grid gap-3 border-b py-6 sm:grid-cols-[10rem_1fr_auto] sm:items-center ${
              themeMode === "dark" ? "border-white/10" : "border-black/10"
            }`}
          >
            <span className="text-sm font-bold opacity-50">
              {formatDate(issue.issue_date)}
            </span>
            <span>
              <span className="block text-xl font-black group-hover:text-[#5fc47d]">
                {issue.title}
              </span>
              <span className="mt-1 block text-sm opacity-50">{issue.tagline}</span>
            </span>
            <span className="text-sm font-black text-[#5fc47d]">Read issue</span>
          </Link>
        ))}
      </div>
    </section>
  );
}
