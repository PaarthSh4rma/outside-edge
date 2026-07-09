import type { InningsScore, Match } from "../types/match";

export function formatInnings(scores: InningsScore[]) {
  if (scores.length === 0) return "Yet to bat";

  return scores
    .map((innings) => {
      const wickets =
        innings.wickets === null || innings.wickets >= 10
          ? ""
          : `/${innings.wickets}`;
      const declaration = innings.declared ? "d" : "";
      return `${innings.runs}${wickets}${declaration}`;
    })
    .join(" & ");
}

export function matchStatusLabel(match: Match) {
  if (match.status === "live") return "Live";
  if (match.status === "scheduled") return "Upcoming";
  if (match.status === "completed") return "Result";
  return match.status;
}

export function formatMatchStart(value: string) {
  return new Intl.DateTimeFormat("en-AU", {
    weekday: "short",
    day: "numeric",
    month: "short",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}
