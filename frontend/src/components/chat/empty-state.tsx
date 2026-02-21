"use client";

import { FileSearch } from "lucide-react";
import { Button } from "@/components/ui/button";

interface EmptyStateProps {
  onSampleQuestion: (question: string) => void;
}

const sampleQuestions = [
  "What is our remote work policy?",
  "Summarize the Q2 product roadmap",
  "How does the authentication API work?",
];

export function EmptyState({ onSampleQuestion }: EmptyStateProps) {
  return (
    <div className="flex-1 flex items-center justify-center p-6">
      <div className="text-center max-w-md">
        <div className="h-16 w-16 rounded-2xl bg-primary-50 flex items-center justify-center mx-auto mb-4">
          <FileSearch className="h-8 w-8 text-primary" />
        </div>
        <h3 className="text-lg font-semibold mb-2">
          Ask anything about your documents
        </h3>
        <p className="text-sm text-muted-foreground mb-6">
          Upload documents and start asking questions. DocuMind will search
          through your documents and provide accurate, cited answers.
        </p>
        <div className="space-y-2">
          {sampleQuestions.map((question) => (
            <Button
              key={question}
              variant="outline"
              className="w-full text-left justify-start text-sm"
              onClick={() => onSampleQuestion(question)}
            >
              {question}
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
}
