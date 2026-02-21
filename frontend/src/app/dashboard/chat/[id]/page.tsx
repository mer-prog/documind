"use client";

import { use } from "react";
import { ConversationList } from "@/components/chat/conversation-list";
import { ChatInterface } from "@/components/chat/chat-interface";

export default function ConversationPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  return (
    <div className="flex h-[calc(100vh-65px)]">
      <div className="w-[280px] border-r border-slate-200 bg-white">
        <ConversationList activeId={id} />
      </div>
      <div className="flex-1">
        <ChatInterface conversationId={id} />
      </div>
    </div>
  );
}
