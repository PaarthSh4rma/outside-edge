import { useEffect, useState } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import { AppShell } from "./components/AppShell";
import { ArchivePage } from "./pages/ArchivePage";
import { HomePage } from "./pages/HomePage";
import { IssuePage } from "./pages/IssuePage";
import { MatchesPage } from "./pages/MatchesPage";
import type { ThemeMode } from "./types/theme";

export default function App() {
  const [themeMode, setThemeMode] = useState<ThemeMode>(() => {
    const storedTheme = localStorage.getItem("outside-edge-theme");
    return storedTheme === "dark" || storedTheme === "light"
      ? storedTheme
      : "dark";
  });

  useEffect(() => {
    localStorage.setItem("outside-edge-theme", themeMode);
  }, [themeMode]);

  return (
    <BrowserRouter>
      <AppShell
        themeMode={themeMode}
        onToggleTheme={() =>
          setThemeMode((current) => (current === "dark" ? "light" : "dark"))
        }
      >
        <Routes>
          <Route path="/" element={<HomePage themeMode={themeMode} />} />
          <Route
            path="/daily-yorker"
            element={<ArchivePage themeMode={themeMode} />}
          />
          <Route
            path="/daily-yorker/:issueDate"
            element={<IssuePage themeMode={themeMode} />}
          />
          <Route path="/matches" element={<MatchesPage themeMode={themeMode} />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  );
}

function NotFoundPage() {
  return (
    <section className="py-12 sm:py-16">
      <div className="max-w-xl border-l-4 border-[#d7ff3f] py-3 pl-5">
        <p className="text-xs font-black uppercase tracking-[0.2em] text-[#5fc47d]">
          Outside Edge
        </p>
        <h1 className="mt-3 text-3xl font-black sm:text-5xl">Page not found.</h1>
        <p className="mt-3 text-sm leading-6 opacity-60">
          This page is not in the scorebook. Head back home or browse the Daily
          Yorker archive.
        </p>
      </div>
    </section>
  );
}
