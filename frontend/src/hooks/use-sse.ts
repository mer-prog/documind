"use client";

import { fetchEventSource } from "@microsoft/fetch-event-source";
import { useCallback, useRef, useState } from "react";
import { apiClient } from "@/lib/api-client";
import type { ChatChunkEvent, SourceCitation } from "@/types/chat";

export function useSSEChat() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [streamedContent, setStreamedContent] = useState("");
  const [sources, setSources] = useState<SourceCitation[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async (message: string, existingConversationId?: string) => {
      setIsStreaming(true);
      setIsSearching(true);
      setStreamedContent("");
      setSources([]);
      abortControllerRef.current = new AbortController();

      const token = await apiClient.getAuthToken();
      const apiBase = apiClient.getApiBase();

      await fetchEventSource(`${apiBase}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          message,
          conversation_id: existingConversationId || undefined,
        }),
        signal: abortControllerRef.current.signal,
        onmessage(event) {
          try {
            const data: ChatChunkEvent = JSON.parse(event.data);
            if (data.type === "conversation_id") {
              setConversationId(data.conversation_id || null);
            } else if (data.type === "sources") {
              setSources(data.sources || []);
              setIsSearching(false);
            } else if (data.type === "token") {
              setStreamedContent((prev) => prev + (data.content || ""));
            } else if (data.type === "done") {
              setIsStreaming(false);
              setIsSearching(false);
            } else if (data.type === "error") {
              setIsStreaming(false);
              setIsSearching(false);
            }
          } catch {
            // Ignore parse errors
          }
        },
        onerror() {
          setIsStreaming(false);
          setIsSearching(false);
          throw new Error("SSE connection error");
        },
      });
    },
    []
  );

  const cancelStream = useCallback(() => {
    abortControllerRef.current?.abort();
    setIsStreaming(false);
    setIsSearching(false);
  }, []);

  return {
    sendMessage,
    cancelStream,
    isStreaming,
    isSearching,
    streamedContent,
    sources,
    conversationId,
  };
}
