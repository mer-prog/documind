"use client";

import Link from "next/link";
import { Plus, MessageSquare } from "lucide-react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useConversations } from "@/hooks/use-conversations";
import { cn, formatRelativeTime } from "@/lib/utils";

interface ConversationListProps {
  activeId?: string;
}

export function ConversationList({ activeId }: ConversationListProps) {
  const { data: conversations, isLoading } = useConversations();
  const t = useTranslations("chat");
  const tc = useTranslations("common");

  return (
    <div className="flex flex-col h-full">
      <div className="p-3 border-b border-slate-200">
        <Link href="/dashboard/chat">
          <Button variant="outline" size="sm" className="w-full">
            <Plus className="h-4 w-4 mr-2" />
            {t("newChat")}
          </Button>
        </Link>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-2 space-y-1">
          {isLoading ? (
            <div className="p-4 text-center text-sm text-muted-foreground">
              {tc("loading")}
            </div>
          ) : !conversations?.length ? (
            <div className="p-4 text-center text-sm text-muted-foreground">
              {t("noConversations")}
            </div>
          ) : (
            conversations.map((conv) => (
              <Link
                key={conv.id}
                href={`/dashboard/chat/${conv.id}`}
                className={cn(
                  "flex items-start gap-2 rounded-lg px-3 py-2 text-sm transition-colors",
                  activeId === conv.id
                    ? "bg-primary-50 text-primary"
                    : "hover:bg-slate-100"
                )}
              >
                <MessageSquare className="h-4 w-4 mt-0.5 shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{conv.title}</p>
                  <p className="text-xs text-muted-foreground">
                    {t("messages", { count: conv.message_count })} &middot;{" "}
                    {formatRelativeTime(conv.updated_at)}
                  </p>
                </div>
              </Link>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
