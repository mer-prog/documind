"use client";

import { useTranslations } from "next-intl";
import { DocumentList } from "@/components/documents/document-list";
import { UploadDialog } from "@/components/documents/upload-dialog";

export default function DocumentsPage() {
  const t = useTranslations("documents");

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold">{t("title")}</h3>
          <p className="text-sm text-muted-foreground">
            {t("description")}
          </p>
        </div>
        <UploadDialog />
      </div>
      <DocumentList />
    </div>
  );
}
