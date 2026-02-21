"use client";

import { useRouter } from "next/navigation";
import { ConversationList } from "@/components/chat/conversation-list";
import { EmptyState } from "@/components/chat/empty-state";
import { ChatInput } from "@/components/chat/chat-input";
import { useChat } from "@/hooks/use-chat";

export default function ChatPage() {
  const router = useRouter();
  const { sendMessage, isStreaming, activeConversationId } = useChat();

  // Navigate to conversation when one is created
  if (activeConversationId) {
    router.push(`/dashboard/chat/${activeConversationId}`);
  }

  return (
    <div className="flex h-[calc(100vh-65px)]">
      <div className="w-[280px] border-r border-slate-200 bg-white">
        <ConversationList />
      </div>
      <div className="flex-1 flex flex-col">
        <EmptyState onSampleQuestion={sendMessage} />
        <ChatInput
          onSend={sendMessage}
          isStreaming={isStreaming}
        />
      </div>
    </div>
  );
}
