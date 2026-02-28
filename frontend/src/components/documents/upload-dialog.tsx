"use client";

import { useState, useRef } from "react";
import { Upload } from "lucide-react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { useUploadDocument, useIngestDocument } from "@/hooks/use-documents";

export function UploadDialog() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const uploadMutation = useUploadDocument();
  const ingestMutation = useIngestDocument();
  const t = useTranslations("documents");

  async function handleUpload() {
    if (!selectedFile) return;
    setUploading(true);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      const result = await uploadMutation.mutateAsync(formData);
      // Auto-ingest after upload
      if (result && typeof result === "object" && "id" in result) {
        await ingestMutation.mutateAsync((result as { id: string }).id);
      }
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch {
      // Error handled by mutation
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="flex items-center gap-3">
      <input
        ref={fileInputRef}
        type="file"
        accept=".md,.pdf,.docx"
        onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
        className="hidden"
        id="file-upload"
      />
      <Button
        variant="outline"
        onClick={() => fileInputRef.current?.click()}
        disabled={uploading}
      >
        <Upload className="h-4 w-4 mr-2" />
        {selectedFile ? selectedFile.name : t("chooseFile")}
      </Button>
      {selectedFile && (
        <Button onClick={handleUpload} disabled={uploading}>
          {uploading ? t("processing") : t("uploadProcess")}
        </Button>
      )}
    </div>
  );
}
