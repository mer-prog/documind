"use client";

import { FileSearch } from "lucide-react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";

interface EmptyStateProps {
  onSampleQuestion: (question: string) => void;
}

const sampleQuestionKeys = ["sampleQ1", "sampleQ2", "sampleQ3"] as const;

export function EmptyState({ onSampleQuestion }: EmptyStateProps) {
  const t = useTranslations("chat");

  return (
    <div className="flex-1 flex items-center justify-center p-6">
      <div className="text-center max-w-md">
        <div className="h-16 w-16 rounded-2xl bg-primary-50 flex items-center justify-center mx-auto mb-4">
          <FileSearch className="h-8 w-8 text-primary" />
        </div>
        <h3 className="text-lg font-semibold mb-2">
          {t("emptyTitle")}
        </h3>
        <p className="text-sm text-muted-foreground mb-6">
          {t("emptyDescription")}
        </p>
        <div className="space-y-2">
          {sampleQuestionKeys.map((key) => {
            const question = t(key);
            return (
              <Button
                key={key}
                variant="outline"
                className="w-full text-left justify-start text-sm"
                onClick={() => onSampleQuestion(question)}
              >
                {question}
              </Button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
