"use client";

import { FileText, FileType, File, Trash2, Play } from "lucide-react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { formatFileSize, formatRelativeTime } from "@/lib/utils";
import type { Document } from "@/types/document";

interface DocumentCardProps {
  document: Document;
  onDelete: (id: string) => void;
  onIngest: (id: string) => void;
}

const fileIcons: Record<string, typeof FileText> = {
  md: FileText,
  pdf: FileType,
  docx: File,
};

const statusVariants: Record<string, "warning" | "info" | "success" | "destructive"> = {
  pending: "warning",
  processing: "info",
  completed: "success",
  failed: "destructive",
};

export function DocumentCard({ document, onDelete, onIngest }: DocumentCardProps) {
  const Icon = fileIcons[document.file_type] || FileText;
  const t = useTranslations("documents");

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <div className="h-10 w-10 rounded-lg bg-primary-50 flex items-center justify-center shrink-0">
            <Icon className="h-5 w-5 text-primary" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{document.filename}</p>
            <div className="flex items-center gap-2 mt-1">
              <Badge variant={statusVariants[document.status] || "secondary"}>
                {t(`status.${document.status}`)}
              </Badge>
              <span className="text-xs text-muted-foreground">
                {formatFileSize(document.file_size)}
              </span>
            </div>
            <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
              {document.chunk_count > 0 && (
                <span>{t("chunks", { count: document.chunk_count })}</span>
              )}
              <span>{formatRelativeTime(document.created_at)}</span>
            </div>
          </div>
          <div className="flex gap-1">
            {document.status === "pending" && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => onIngest(document.id)}
                title={t("processDocument")}
              >
                <Play className="h-4 w-4 text-primary" />
              </Button>
            )}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => onDelete(document.id)}
              title={t("deleteDocument")}
            >
              <Trash2 className="h-4 w-4 text-red-500" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
