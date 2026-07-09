import { MatchSection } from "../components/MatchSection";
import { useMatches } from "../hooks/useMatches";
import type { ThemeMode } from "../types/theme";

export function MatchesPage({ themeMode }: { themeMode: ThemeMode }) {
  const live = useMatches("live");
  const upcoming = useMatches("upcoming");
  const recent = useMatches("recent");

  return (
    <div className="py-8 sm:py-12">
      <header className="max-w-3xl border-b border-current/10 pb-8 sm:pb-10">
        <p className="text-xs font-black uppercase tracking-[0.2em] text-[#5fc47d]">
          Match centre
        </p>
        <h1 className="mt-4 text-4xl font-black tracking-normal sm:text-6xl">
          Scores without the clutter.
        </h1>
        <p className="mt-5 text-base leading-7 opacity-60 sm:text-lg">
          Live positions, what is coming next, and the latest results from
          across world cricket.
        </p>
      </header>

      <div className="mt-10 space-y-12 sm:mt-12 sm:space-y-16">
        <MatchSection
          eyebrow="In play"
          title="Live"
          description="Matches currently under way."
          emptyMessage="The next live match will appear here when play begins."
          themeMode={themeMode}
          {...live}
        />
        <MatchSection
          eyebrow="On the calendar"
          title="Upcoming"
          description="The next fixtures worth keeping an eye on."
          emptyMessage="No upcoming fixtures are available yet."
          themeMode={themeMode}
          {...upcoming}
        />
        <MatchSection
          eyebrow="Final scores"
          title="Recent"
          description="Recently completed matches and their results."
          emptyMessage="Completed matches will be collected here."
          themeMode={themeMode}
          {...recent}
        />
      </div>
    </div>
  );
}
