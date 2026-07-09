import type { Match } from "../types/match";
import type { ThemeMode } from "../types/theme";
import {
  formatInnings,
  formatMatchStart,
  matchStatusLabel,
} from "../utils/match";

export function MatchCard({
  match,
  themeMode,
}: {
  match: Match;
  themeMode: ThemeMode;
}) {
  const snapshot = match.latest_score;

  return (
    <article
      className={
        themeMode === "dark"
          ? "border border-white/10 bg-white/[0.03] p-5"
          : "border border-black/10 bg-white p-5"
      }
    >
      <div className="flex items-start justify-between gap-3">
        <span
          className={`text-xs font-black uppercase ${
            match.status === "live" ? "text-[#d7ff3f]" : "opacity-50"
          }`}
        >
          {matchStatusLabel(match)}
        </span>
        <span className="text-right text-xs font-bold opacity-45">
          {match.format} · {match.competition.short_name ?? match.competition.name}
        </span>
      </div>

      <div className="mt-6 space-y-3">
        <TeamScore
          name={match.home_team.name}
          shortName={match.home_team.short_name}
          score={snapshot ? formatInnings(snapshot.home_score) : "Yet to bat"}
          showScore={match.status !== "scheduled"}
        />
        <TeamScore
          name={match.away_team.name}
          shortName={match.away_team.short_name}
          score={snapshot ? formatInnings(snapshot.away_score) : "Yet to bat"}
          showScore={match.status !== "scheduled"}
        />
      </div>

      <div className="mt-6 border-t border-current/10 pt-4">
        <p className="text-sm font-bold">
          {snapshot?.status_text ?? formatMatchStart(match.starts_at)}
        </p>
        <p className="mt-1 text-xs leading-5 opacity-50">
          {match.status === "scheduled"
            ? formatMatchStart(match.starts_at)
            : snapshot?.detail}
          {match.venue ? ` · ${match.venue}` : ""}
        </p>
        {match.is_stale && (
          <p className="mt-3 text-xs font-black uppercase text-amber-500">
            Score update delayed
          </p>
        )}
      </div>
    </article>
  );
}

function TeamScore({
  name,
  shortName,
  score,
  showScore,
}: {
  name: string;
  shortName: string;
  score: string;
  showScore: boolean;
}) {
  return (
    <div className="grid grid-cols-[1fr_auto] items-baseline gap-3">
      <p className="min-w-0 truncate font-black" title={name}>
        <span className="sm:hidden">{shortName}</span>
        <span className="hidden sm:inline">{name}</span>
      </p>
      <p className="text-lg font-black">{showScore ? score : shortName}</p>
    </div>
  );
}
