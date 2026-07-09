export type InningsScore = {
  innings_number: number;
  runs: number;
  wickets: number | null;
  overs: string;
  declared: boolean;
};

export type ScoreSnapshot = {
  id: number;
  home_score: InningsScore[];
  away_score: InningsScore[];
  status_text: string;
  detail: string | null;
  captured_at: string;
};

export type Match = {
  id: number;
  competition: {
    id: number;
    name: string;
    short_name: string | null;
    country: string | null;
    season: string | null;
  };
  home_team: {
    id: number;
    name: string;
    short_name: string;
  };
  away_team: {
    id: number;
    name: string;
    short_name: string;
  };
  status: "scheduled" | "live" | "completed" | "abandoned" | "cancelled";
  format: string;
  starts_at: string;
  venue: string | null;
  result_summary: string | null;
  latest_score: ScoreSnapshot | null;
  is_stale: boolean;
};

export type MatchGroup = "live" | "upcoming" | "recent";
