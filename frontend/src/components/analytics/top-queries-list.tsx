"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { TopQuery } from "@/types/analytics";

interface TopQueriesListProps {
  data: TopQuery[];
}

export function TopQueriesList({ data }: TopQueriesListProps) {
  const maxCount = data.length > 0 ? data[0].count : 1;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Top Queries</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {data.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              No queries yet
            </p>
          ) : (
            data.map((query, index) => (
              <div key={index} className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <span className="truncate flex-1 mr-2">{query.query}</span>
                  <span className="text-muted-foreground shrink-0">
                    {query.count}
                  </span>
                </div>
                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full transition-all"
                    style={{ width: `${(query.count / maxCount) * 100}%` }}
                  />
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
