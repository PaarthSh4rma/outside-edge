import { Link } from "react-router-dom";

import { useMatches } from "../hooks/useMatches";
import type { ThemeMode } from "../types/theme";
import { MatchCard } from "./MatchCard";
import { MatchState } from "./MatchState";

export function ScoreSection({ themeMode }: { themeMode: ThemeMode }) {
  const live = useMatches("live");
  const upcoming = useMatches("upcoming");
  const matches = [...live.matches, ...upcoming.matches].slice(0, 3);
  const isLoading = live.isLoading || upcoming.isLoading;
  const hasError = live.hasError && upcoming.hasError;

  return (
    <section className="mt-10" aria-labelledby="scores-heading">
      <div className="mb-4 flex items-end justify-between gap-4">
        <div>
          <p className="text-xs font-black uppercase tracking-[0.2em] text-[#5fc47d]">
            Match centre
          </p>
          <h2 id="scores-heading" className="mt-2 text-2xl font-black sm:text-3xl">
            On the field
          </h2>
        </div>
        <Link
          to="/matches"
          className="text-xs font-black uppercase text-[#5fc47d] hover:underline"
        >
          All matches
        </Link>
      </div>

      {isLoading && matches.length === 0 && (
        <MatchState
          title="Loading the match centre..."
          message="Checking live and upcoming cricket."
          themeMode={themeMode}
          compact
        />
      )}
      {!isLoading && hasError && matches.length === 0 && (
        <MatchState
          title="The match centre is temporarily unavailable."
          message="Outside Edge could not reach the score service. Please try again shortly."
          themeMode={themeMode}
          compact
        />
      )}
      {!isLoading && !hasError && matches.length === 0 && (
        <MatchState
          title="A quiet moment between overs."
          message="There are no live or upcoming matches to show right now."
          themeMode={themeMode}
          compact
        />
      )}
      {matches.length > 0 && (
        <div className="grid gap-3 md:grid-cols-3">
          {matches.map((match) => (
            <MatchCard key={match.id} match={match} themeMode={themeMode} />
          ))}
        </div>
      )}
    </section>
  );
}
