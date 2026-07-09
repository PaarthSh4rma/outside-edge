import { MatchCard } from "./MatchCard";
import { MatchState } from "./MatchState";
import type { Match } from "../types/match";
import type { ThemeMode } from "../types/theme";

export function MatchSection({
  eyebrow,
  title,
  description,
  matches,
  isLoading,
  hasError,
  emptyMessage,
  themeMode,
}: {
  eyebrow: string;
  title: string;
  description: string;
  matches: Match[];
  isLoading: boolean;
  hasError: boolean;
  emptyMessage: string;
  themeMode: ThemeMode;
}) {
  return (
    <section>
      <header className="mb-5 max-w-2xl">
        <p className="text-xs font-black uppercase tracking-[0.2em] text-[#5fc47d]">
          {eyebrow}
        </p>
        <h2 className="mt-2 text-2xl font-black sm:text-3xl">{title}</h2>
        <p className="mt-2 text-sm leading-6 opacity-55">{description}</p>
      </header>

      {isLoading && (
        <MatchState
          title={`Loading ${title.toLowerCase()}...`}
          message="Checking the latest match information."
          themeMode={themeMode}
        />
      )}
      {!isLoading && hasError && (
        <MatchState
          title="The match desk is temporarily unavailable."
          message="Outside Edge could not reach the score service. Please try again shortly."
          themeMode={themeMode}
        />
      )}
      {!isLoading && !hasError && matches.length === 0 && (
        <MatchState
          title={`No ${title.toLowerCase()} right now.`}
          message={emptyMessage}
          themeMode={themeMode}
        />
      )}
      {!isLoading && !hasError && matches.length > 0 && (
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {matches.map((match) => (
            <MatchCard key={match.id} match={match} themeMode={themeMode} />
          ))}
        </div>
      )}
    </section>
  );
}
