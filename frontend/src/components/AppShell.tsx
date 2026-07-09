import type { ReactNode } from "react";
import { Link, NavLink } from "react-router-dom";

import type { ThemeMode } from "../types/theme";

type AppShellProps = {
  children: ReactNode;
  themeMode: ThemeMode;
  onToggleTheme: () => void;
};

export function AppShell({
  children,
  themeMode,
  onToggleTheme,
}: AppShellProps) {
  return (
    <main
      className={
        themeMode === "dark"
          ? "min-h-screen bg-[#101513] text-white"
          : "min-h-screen bg-[#f5f7f5] text-[#17211b]"
      }
    >
      <div className="pointer-events-none fixed inset-0 bg-[linear-gradient(90deg,transparent_0%,transparent_49.9%,rgba(45,90,64,0.08)_50%,transparent_50.1%)]" />
      <div className="relative mx-auto min-h-screen w-full max-w-7xl px-4 py-4 sm:px-6 sm:py-6 lg:px-8">
        <header
          className={
            themeMode === "dark"
              ? "sticky top-3 z-50 mb-6 flex items-center justify-between gap-4 border border-white/10 bg-[#101513]/95 px-4 py-3 shadow-xl backdrop-blur sm:top-4"
              : "sticky top-3 z-50 mb-6 flex items-center justify-between gap-4 border border-black/10 bg-white/95 px-4 py-3 shadow-sm backdrop-blur sm:top-4"
          }
        >
          <Link to="/" className="flex min-w-0 items-center gap-3">
            <span className="flex h-10 w-10 shrink-0 items-center justify-center bg-[#d7ff3f] text-sm font-black text-[#17211b]">
              OE
            </span>
            <span className="min-w-0">
              <span className="block truncate text-sm font-black uppercase tracking-[0.18em]">
                Outside Edge
              </span>
              <span className={mutedText(themeMode)}>Cricket intelligence</span>
            </span>
          </Link>

          <div className="flex items-center gap-2">
            <nav className="hidden items-center sm:flex">
              <NavItem to="/" label="Home" />
              <NavItem to="/daily-yorker" label="Daily Yorker" />
            </nav>
            <button
              type="button"
              onClick={onToggleTheme}
              className={
                themeMode === "dark"
                  ? "min-h-10 border border-white/15 px-3 text-sm font-bold hover:bg-white/10"
                  : "min-h-10 border border-black/15 px-3 text-sm font-bold hover:bg-black/5"
              }
              aria-label={`Switch to ${themeMode === "dark" ? "light" : "dark"} mode`}
            >
              {themeMode === "dark" ? "Light" : "Dark"}
            </button>
          </div>
        </header>

        {children}

        <footer
          className={`mt-12 border-t py-7 text-sm ${
            themeMode === "dark"
              ? "border-white/10 text-white/55"
              : "border-black/10 text-black/55"
          }`}
        >
          <div className="flex flex-wrap justify-between gap-3">
            <p>Outside Edge. Cricket, without the noise.</p>
            <Link to="/daily-yorker" className="font-bold hover:underline">
              Daily Yorker archive
            </Link>
          </div>
        </footer>
      </div>
    </main>
  );
}

function NavItem({ to, label }: { to: string; label: string }) {
  return (
    <NavLink
      to={to}
      end={to === "/"}
      className={({ isActive }) =>
        `px-3 py-2 text-sm font-bold ${
          isActive ? "text-[#72d690]" : "opacity-65 hover:opacity-100"
        }`
      }
    >
      {label}
    </NavLink>
  );
}

function mutedText(themeMode: ThemeMode) {
  return themeMode === "dark"
    ? "text-sm text-white/60"
    : "text-sm text-black/60";
}
