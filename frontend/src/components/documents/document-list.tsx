"use client";

import { useDocuments, useDeleteDocument, useIngestDocument } from "@/hooks/use-documents";
import { DocumentCard } from "./document-card";
import { Skeleton } from "@/components/ui/skeleton";

export function DocumentList() {
  const { data, isLoading } = useDocuments();
  const deleteMutation = useDeleteDocument();
  const ingestMutation = useIngestDocument();

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[...Array(6)].map((_, i) => (
          <Skeleton key={i} className="h-32 rounded-lg" />
        ))}
      </div>
    );
  }

  if (!data?.documents?.length) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">
          No documents uploaded yet. Upload your first document to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {data.documents.map((doc) => (
        <DocumentCard
          key={doc.id}
          document={doc}
          onDelete={(id) => deleteMutation.mutate(id)}
          onIngest={(id) => ingestMutation.mutate(id)}
        />
      ))}
    </div>
  );
}
