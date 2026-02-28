"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useLocale, useTranslations } from "next-intl";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatLocalDate } from "@/lib/utils";
import type { UsageDataPoint } from "@/types/analytics";

interface LatencyChartProps {
  data: UsageDataPoint[];
}

export function LatencyChart({ data }: LatencyChartProps) {
  const t = useTranslations("analytics");
  const locale = useLocale();

  const chartData = data.map((d) => ({
    date: formatLocalDate(d.date, locale),
    latency: Math.round(d.avg_latency_ms),
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{t("averageLatency")}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12 }}
                stroke="#94a3b8"
              />
              <YAxis
                tick={{ fontSize: 12 }}
                stroke="#94a3b8"
                unit={t("ms")}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "white",
                  border: "1px solid #e2e8f0",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
                formatter={(value: number) => [`${value}${t("ms")}`, t("latency")]}
              />
              <Line
                type="monotone"
                dataKey="latency"
                name={t("latency")}
                stroke="#4F46E5"
                strokeWidth={2}
                dot={{ fill: "#4F46E5", r: 3 }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
