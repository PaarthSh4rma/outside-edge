import { useEffect, useState } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import { AppShell } from "./components/AppShell";
import { ArchivePage } from "./pages/ArchivePage";
import { HomePage } from "./pages/HomePage";
import { IssuePage } from "./pages/IssuePage";
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
        </Routes>
      </AppShell>
    </BrowserRouter>
  );
}
