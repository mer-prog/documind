"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { ConversationDetail, ConversationSummary } from "@/types/conversation";

export function useConversations() {
  return useQuery({
    queryKey: ["conversations"],
    queryFn: () =>
      apiClient.get<ConversationSummary[]>("/api/conversations"),
  });
}

export function useConversation(id: string) {
  return useQuery({
    queryKey: ["conversation", id],
    queryFn: () =>
      apiClient.get<ConversationDetail>(`/api/conversations/${id}`),
    enabled: !!id,
  });
}
