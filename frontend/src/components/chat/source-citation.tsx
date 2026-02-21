"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight, FileText } from "lucide-react";
import type { SourceCitation as SourceCitationType } from "@/types/chat";

interface SourceCitationProps {
  source: SourceCitationType;
}

export function SourceCitation({ source }: SourceCitationProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="border-l-2 border-primary-300 bg-slate-50 rounded-r-lg overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 w-full px-3 py-2 text-left hover:bg-slate-100 transition-colors"
      >
        {isOpen ? (
          <ChevronDown className="h-3 w-3 text-muted-foreground shrink-0" />
        ) : (
          <ChevronRight className="h-3 w-3 text-muted-foreground shrink-0" />
        )}
        <FileText className="h-3 w-3 text-primary shrink-0" />
        <span className="text-xs font-medium text-slate-700 truncate">
          {source.document_name}
        </span>
        {source.page_number && (
          <span className="text-xs text-muted-foreground">
            Page {source.page_number}
          </span>
        )}
      </button>
      {isOpen && (
        <div className="px-3 pb-3">
          <p className="text-xs text-slate-600 leading-relaxed">
            {source.text_snippet}
          </p>
        </div>
      )}
    </div>
  );
}
