"use client";

import { useUsageAnalytics, useTopQueries } from "@/hooks/use-analytics";
import { TokenUsageChart } from "@/components/analytics/token-usage-chart";
import { QueryCountChart } from "@/components/analytics/query-count-chart";
import { LatencyChart } from "@/components/analytics/latency-chart";
import { TopQueriesList } from "@/components/analytics/top-queries-list";
import { Skeleton } from "@/components/ui/skeleton";

export default function AnalyticsPage() {
  const { data: usage, isLoading: usageLoading } = useUsageAnalytics();
  const { data: topQueries, isLoading: queriesLoading } = useTopQueries();

  if (usageLoading || queriesLoading) {
    return (
      <div className="p-6 space-y-6">
        <h1 className="text-2xl font-bold">Analytics</h1>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-[380px] rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Analytics</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TokenUsageChart data={usage?.data || []} />
        <QueryCountChart data={usage?.data || []} />
        <LatencyChart data={usage?.data || []} />
        <TopQueriesList data={topQueries?.queries || []} />
      </div>
    </div>
  );
}
