import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { ApiError, apiGet } from "../api/client";
import { IssueView } from "../components/IssueView";
import { ScoreSection } from "../components/ScoreSection";
import { SubscribeSection } from "../components/SubscribeSection";
import type { Issue } from "../types/issue";
import type { ThemeMode } from "../types/theme";

export function HomePage({ themeMode }: { themeMode: ThemeMode }) {
  const [issue, setIssue] = useState<Issue | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadState, setLoadState] = useState<"ready" | "empty" | "unavailable">(
    "ready",
  );

  useEffect(() => {
    apiGet<Issue>("/issues/latest")
      .then(setIssue)
      .catch((error: unknown) => {
        setLoadState(error instanceof ApiError && error.status === 404 ? "empty" : "unavailable");
      })
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <>
      <section className="grid min-h-[58vh] items-end gap-8 border-b border-current/10 pb-10 pt-10 lg:min-h-[50vh] lg:grid-cols-[1.5fr_0.5fr] lg:pb-8 lg:pt-12">
        <div>
          <p className="text-xs font-black uppercase tracking-[0.2em] text-[#5fc47d]">
            Ad-free cricket intelligence
          </p>
          <h1 className="mt-4 max-w-4xl text-5xl font-black leading-[0.98] tracking-normal sm:text-6xl md:text-7xl">
            Know the game beyond the score.
          </h1>
          <p className="mt-6 max-w-2xl text-base leading-7 opacity-65 sm:text-lg">
            The stories, context and signals shaping world cricket, gathered into
            one considered daily read.
          </p>
        </div>
        <div className="border-l-4 border-[#d7ff3f] pl-5">
          <p className="text-sm font-bold opacity-55">Today's briefing</p>
          <p className="mt-2 text-2xl font-black">
            {issue
              ? `${countArticles(issue)} stories selected`
              : isLoading
                ? "Checking today's briefing..."
                : loadState === "empty"
                  ? "Today's briefing is being prepared."
                  : "Briefing status unavailable."}
          </p>
          {!issue && !isLoading && (
            <p className="mt-2 max-w-xs text-sm leading-6 opacity-55">
              {loadState === "empty"
                ? "Check back shortly."
                : "Outside Edge could not reach the briefing service."}
            </p>
          )}
          <Link
            to="/daily-yorker"
            className="mt-5 inline-block text-sm font-black text-[#5fc47d] hover:underline"
          >
            Browse the archive
          </Link>
        </div>
      </section>

      <div className="lg:[&>section]:mt-8">
        <ScoreSection themeMode={themeMode} />
      </div>

      <section
        className={
          themeMode === "dark"
            ? "mt-12 border border-white/10 bg-[#151d19] p-5 sm:p-8 md:p-10 lg:mt-10"
            : "mt-12 border border-black/10 bg-white p-5 sm:p-8 md:p-10 lg:mt-10"
        }
      >
        {isLoading && <p className="text-sm opacity-60">Loading today's dispatch...</p>}
        {!isLoading && loadState === "empty" && (
          <EmptyBriefing
            title="Today's briefing is being prepared."
            message="Check back shortly. The first Daily Yorker will appear here as soon as it is published."
          />
        )}
        {!isLoading && loadState === "unavailable" && (
          <EmptyBriefing
            title="The pavilion is temporarily closed."
            message="Outside Edge could not reach the briefing service. Please try again shortly."
          />
        )}
        {issue && <IssueView issue={issue} themeMode={themeMode} compact />}
      </section>

      <SubscribeSection themeMode={themeMode} />
    </>
  );
}

function EmptyBriefing({ title, message }: { title: string; message: string }) {
  return (
    <div className="max-w-xl py-4 sm:py-6">
      <p className="text-xs font-black uppercase tracking-[0.2em] text-[#5fc47d]">
        The Daily Yorker
      </p>
      <h2 className="mt-3 text-2xl font-black sm:text-3xl">{title}</h2>
      <p className="mt-3 text-sm leading-6 opacity-60">{message}</p>
    </div>
  );
}

function countArticles(issue: Issue) {
  return issue.sections.reduce((total, section) => total + section.articles.length, 0);
}
