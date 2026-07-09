import type { ThemeMode } from "../types/theme";

const placeholderMatches = [
  {
    status: "Live",
    competition: "Test series",
    teams: "Australia v India",
    score: "AUS 218/5",
    detail: "Day 2, Session 3",
  },
  {
    status: "Upcoming",
    competition: "Women's ODI",
    teams: "England v New Zealand",
    score: "Tomorrow",
    detail: "10:00 local",
  },
  {
    status: "Upcoming",
    competition: "T20 series",
    teams: "South Africa v Pakistan",
    score: "Sat 11 Jul",
    detail: "19:30 local",
  },
];

export function ScoreSection({ themeMode }: { themeMode: ThemeMode }) {
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
        <span className="text-xs font-bold uppercase opacity-45">Preview data</span>
      </div>

      <div className="grid gap-3 md:grid-cols-3">
        {placeholderMatches.map((match) => (
          <article
            key={match.teams}
            className={
              themeMode === "dark"
                ? "border border-white/10 bg-white/[0.03] p-5"
                : "border border-black/10 bg-white p-5"
            }
          >
            <div className="flex items-center justify-between gap-2">
              <span
                className={`text-xs font-black uppercase ${
                  match.status === "Live" ? "text-[#d7ff3f]" : "opacity-50"
                }`}
              >
                {match.status}
              </span>
              <span className="text-xs font-bold opacity-45">
                {match.competition}
              </span>
            </div>
            <h3 className="mt-7 text-base font-black">{match.teams}</h3>
            <p className="mt-2 text-2xl font-black">{match.score}</p>
            <p className="mt-1 text-sm opacity-50">{match.detail}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
