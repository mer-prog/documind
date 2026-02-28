"use client";

import { FileText, MessageSquare, Activity, Zap } from "lucide-react";
import { useTranslations } from "next-intl";
import { StatCard } from "@/components/dashboard/stat-card";
import { useDocuments } from "@/hooks/use-documents";
import { useConversations } from "@/hooks/use-conversations";
import { useUsageAnalytics } from "@/hooks/use-analytics";

export default function DashboardPage() {
  const { data: documents } = useDocuments();
  const { data: conversations } = useConversations();
  const { data: usage } = useUsageAnalytics(30);
  const t = useTranslations("dashboard");

  return (
    <div className="p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold">{t("workspaceOverview")}</h3>
        <p className="text-sm text-muted-foreground">
          {t("workspaceDescription")}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title={t("documentsTitle")}
          value={documents?.total ?? 0}
          icon={FileText}
          description={t("totalDocuments")}
        />
        <StatCard
          title={t("conversationsTitle")}
          value={conversations?.length ?? 0}
          icon={MessageSquare}
          description={t("chatConversations")}
        />
        <StatCard
          title={t("queriesThisMonth")}
          value={usage?.total_queries ?? 0}
          icon={Activity}
          description={t("totalQueries")}
        />
        <StatCard
          title={t("tokensUsed")}
          value={
            usage?.total_tokens
              ? `${(usage.total_tokens / 1000).toFixed(1)}k`
              : "0"
          }
          icon={Zap}
          description={t("monthlyTokens")}
        />
      </div>
    </div>
  );
}
