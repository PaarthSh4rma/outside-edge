import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ApiError, apiGet } from "../api/client";
import { IssueView } from "../components/IssueView";
import type { Issue } from "../types/issue";
import type { ThemeMode } from "../types/theme";

export function IssuePage({ themeMode }: { themeMode: ThemeMode }) {
  const { issueDate } = useParams();
  const [issue, setIssue] = useState<Issue | null>(null);
  const [loadState, setLoadState] = useState<"loading" | "not-found" | "unavailable">(
    "loading",
  );

  useEffect(() => {
    if (!issueDate) return;

    apiGet<Issue>(`/issues/${issueDate}`)
      .then((loadedIssue) => {
        setIssue(loadedIssue);
      })
      .catch((error: unknown) => {
        setLoadState(
          error instanceof ApiError && error.status === 404
            ? "not-found"
            : "unavailable",
        );
      });
  }, [issueDate]);

  return (
    <section className="py-8 sm:py-12">
      <Link
        to="/daily-yorker"
        className="mb-8 inline-block text-sm font-black text-[#5fc47d] hover:underline"
      >
        Back to archive
      </Link>
      {!issue && loadState === "loading" && (
        <p className="text-sm opacity-60">Loading issue...</p>
      )}
      {!issue && loadState === "not-found" && (
        <IssueMessage
          title="This Yorker missed the stumps."
          message="No issue was published for this date."
        />
      )}
      {!issue && loadState === "unavailable" && (
        <IssueMessage
          title="The scorebook is temporarily unavailable."
          message="Outside Edge could not reach the archive service. Please try again shortly."
        />
      )}
      {issue && (
        <div
          className={
            themeMode === "dark"
              ? "border border-white/10 bg-[#151d19] p-5 sm:p-8 md:p-10"
              : "border border-black/10 bg-white p-5 sm:p-8 md:p-10"
          }
        >
          <IssueView issue={issue} themeMode={themeMode} />
        </div>
      )}
    </section>
  );
}

function IssueMessage({ title, message }: { title: string; message: string }) {
  return (
    <div className="max-w-xl border-l-4 border-[#d7ff3f] py-3 pl-5">
      <h1 className="text-2xl font-black sm:text-3xl">{title}</h1>
      <p className="mt-2 text-sm leading-6 opacity-60">{message}</p>
    </div>
  );
}
