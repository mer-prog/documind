"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { TopQueriesResponse, UsageResponse } from "@/types/analytics";

export function useUsageAnalytics(days = 30) {
  return useQuery({
    queryKey: ["analytics", "usage", days],
    queryFn: () =>
      apiClient.get<UsageResponse>(`/api/analytics/usage?days=${days}`),
  });
}

export function useTopQueries(days = 30) {
  return useQuery({
    queryKey: ["analytics", "top-queries", days],
    queryFn: () =>
      apiClient.get<TopQueriesResponse>(
        `/api/analytics/top-queries?days=${days}`
      ),
  });
}
