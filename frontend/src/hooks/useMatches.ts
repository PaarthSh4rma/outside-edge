import { useEffect, useState } from "react";

import { apiGet } from "../api/client";
import type { Match, MatchGroup } from "../types/match";

export function useMatches(group: MatchGroup) {
  const [matches, setMatches] = useState<Match[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    let isCancelled = false;

    apiGet<Match[]>(`/matches/${group}`)
      .then((loadedMatches) => {
        if (!isCancelled) setMatches(loadedMatches);
      })
      .catch(() => {
        if (!isCancelled) setHasError(true);
      })
      .finally(() => {
        if (!isCancelled) setIsLoading(false);
      });

    return () => {
      isCancelled = true;
    };
  }, [group]);

  return { matches, isLoading, hasError };
}
