"use client";

import { useTranslations } from "next-intl";

export function ThinkingIndicator() {
  const t = useTranslations("chat");

  return (
    <div className="flex items-center gap-2 text-slate-500 py-3 px-4">
      <div className="flex gap-1">
        <span
          className="w-2 h-2 bg-primary-400 rounded-full animate-bounce"
          style={{ animationDelay: "0ms" }}
        />
        <span
          className="w-2 h-2 bg-primary-400 rounded-full animate-bounce"
          style={{ animationDelay: "150ms" }}
        />
        <span
          className="w-2 h-2 bg-primary-400 rounded-full animate-bounce"
          style={{ animationDelay: "300ms" }}
        />
      </div>
      <span className="text-sm">{t("thinking")}</span>
    </div>
  );
}
