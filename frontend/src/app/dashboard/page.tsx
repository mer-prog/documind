"use client";

import { FileText, MessageSquare, Activity, Zap } from "lucide-react";
import { StatCard } from "@/components/dashboard/stat-card";
import { useDocuments } from "@/hooks/use-documents";
import { useConversations } from "@/hooks/use-conversations";
import { useUsageAnalytics } from "@/hooks/use-analytics";

export default function DashboardPage() {
  const { data: documents } = useDocuments();
  const { data: conversations } = useConversations();
  const { data: usage } = useUsageAnalytics(30);

  return (
    <div className="p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold">Workspace Overview</h3>
        <p className="text-sm text-muted-foreground">
          Your document intelligence at a glance
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Documents"
          value={documents?.total ?? 0}
          icon={FileText}
          description="Total uploaded documents"
        />
        <StatCard
          title="Conversations"
          value={conversations?.length ?? 0}
          icon={MessageSquare}
          description="Chat conversations"
        />
        <StatCard
          title="Queries This Month"
          value={usage?.total_queries ?? 0}
          icon={Activity}
          description="Total search queries"
        />
        <StatCard
          title="Tokens Used"
          value={
            usage?.total_tokens
              ? `${(usage.total_tokens / 1000).toFixed(1)}k`
              : "0"
          }
          icon={Zap}
          description="Monthly token consumption"
        />
      </div>
    </div>
  );
}
