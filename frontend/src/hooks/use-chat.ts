"use client";

import { useCallback, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useSSEChat } from "./use-sse";
import type { Message } from "@/types/conversation";
import type { SourceCitation } from "@/types/chat";

export function useChat(initialConversationId?: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<
    string | undefined
  >(initialConversationId);
  const queryClient = useQueryClient();

  const {
    sendMessage: sseSendMessage,
    cancelStream,
    isStreaming,
    isSearching,
    streamedContent,
    sources,
    conversationId: newConversationId,
  } = useSSEChat();

  const sendMessage = useCallback(
    async (content: string) => {
      // Add user message immediately
      const userMessage: Message = {
        id: `temp-${Date.now()}`,
        role: "user",
        content,
        sources: null,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);

      // Send via SSE
      await sseSendMessage(content, activeConversationId);

      // Update conversation ID if new
      if (newConversationId && !activeConversationId) {
        setActiveConversationId(newConversationId);
      }

      // Invalidate conversations list
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
    },
    [activeConversationId, sseSendMessage, newConversationId, queryClient]
  );

  const addAssistantMessage = useCallback(
    (content: string, messageSources: SourceCitation[]) => {
      const assistantMessage: Message = {
        id: `temp-${Date.now()}`,
        role: "assistant",
        content,
        sources: messageSources.length > 0 ? messageSources : null,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    },
    []
  );

  return {
    messages,
    setMessages,
    sendMessage,
    cancelStream,
    addAssistantMessage,
    isStreaming,
    isSearching,
    streamedContent,
    sources,
    activeConversationId: newConversationId || activeConversationId,
  };
}
