"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { UsageDataPoint } from "@/types/analytics";

interface TokenUsageChartProps {
  data: UsageDataPoint[];
}

export function TokenUsageChart({ data }: TokenUsageChartProps) {
  const chartData = data.map((d) => ({
    date: new Date(d.date).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }),
    prompt: d.tokens_prompt,
    completion: d.tokens_completion,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Token Usage</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12 }}
                stroke="#94a3b8"
              />
              <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "white",
                  border: "1px solid #e2e8f0",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="prompt"
                name="Prompt Tokens"
                stackId="1"
                stroke="#4F46E5"
                fill="#4F46E5"
                fillOpacity={0.6}
              />
              <Area
                type="monotone"
                dataKey="completion"
                name="Completion Tokens"
                stackId="1"
                stroke="#10B981"
                fill="#10B981"
                fillOpacity={0.6}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
