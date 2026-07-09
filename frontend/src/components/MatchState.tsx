import type { ThemeMode } from "../types/theme";

export function MatchState({
  title,
  message,
  themeMode,
  compact = false,
}: {
  title: string;
  message: string;
  themeMode: ThemeMode;
  compact?: boolean;
}) {
  return (
    <div
      className={`border ${
        themeMode === "dark"
          ? "border-white/10 bg-white/[0.03]"
          : "border-black/10 bg-white"
      } ${compact ? "p-5" : "p-6 sm:p-8"}`}
    >
      <p className="font-black">{title}</p>
      <p className="mt-2 text-sm leading-6 opacity-55">{message}</p>
    </div>
  );
}
