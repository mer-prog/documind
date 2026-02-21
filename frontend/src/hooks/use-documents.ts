"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { DocumentListResponse, IngestResponse } from "@/types/document";

export function useDocuments() {
  return useQuery({
    queryKey: ["documents"],
    queryFn: () => apiClient.get<DocumentListResponse>("/api/documents"),
  });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (formData: FormData) =>
      apiClient.upload<Document>("/api/documents", formData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (documentId: string) =>
      apiClient.delete(`/api/documents/${documentId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });
}

export function useIngestDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (documentId: string) =>
      apiClient.post<IngestResponse>(`/api/documents/${documentId}/ingest`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });
}
