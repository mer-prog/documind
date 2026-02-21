"use client";

import { DocumentList } from "@/components/documents/document-list";
import { UploadDialog } from "@/components/documents/upload-dialog";

export default function DocumentsPage() {
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold">Documents</h3>
          <p className="text-sm text-muted-foreground">
            Upload and manage your documents
          </p>
        </div>
        <UploadDialog />
      </div>
      <DocumentList />
    </div>
  );
}
