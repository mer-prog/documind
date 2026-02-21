"use client";

import { useEffect, useRef } from "react";
import { useConversation } from "@/hooks/use-conversations";
import { useChat } from "@/hooks/use-chat";
import { MessageBubble } from "./message-bubble";
import { ChatInput } from "./chat-input";
import { ThinkingIndicator } from "./thinking-indicator";
import type { Message } from "@/types/conversation";

interface ChatInterfaceProps {
  conversationId?: string;
}

export function ChatInterface({ conversationId }: ChatInterfaceProps) {
  const { data: conversation } = useConversation(conversationId || "");
  const {
    messages: localMessages,
    setMessages,
    sendMessage,
    cancelStream,
    isStreaming,
    isSearching,
    streamedContent,
    sources,
  } = useChat(conversationId);

  const scrollRef = useRef<HTMLDivElement>(null);

  // Sync conversation messages on load
  useEffect(() => {
    if (conversation?.messages) {
      setMessages(conversation.messages);
    }
  }, [conversation?.messages, setMessages]);

  // Auto-scroll on new content
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [localMessages, streamedContent]);

  // Build display messages
  const displayMessages: Message[] = [...localMessages];

  // Add streaming message if active
  if (isStreaming && streamedContent) {
    displayMessages.push({
      id: "streaming",
      role: "assistant",
      content: streamedContent,
      sources: sources.length > 0 ? sources : null,
      created_at: new Date().toISOString(),
    });
  }

  return (
    <div className="flex flex-col h-full">
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 space-y-4 max-w-3xl mx-auto w-full"
      >
        {displayMessages.map((msg) => (
          <MessageBubble
            key={msg.id}
            message={msg}
            isStreaming={msg.id === "streaming"}
          />
        ))}
        {isSearching && <ThinkingIndicator />}
      </div>

      <ChatInput
        onSend={sendMessage}
        onCancel={cancelStream}
        isStreaming={isStreaming}
      />
    </div>
  );
}
