"use client";

import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { LanguageToggle } from "@/components/language-toggle";

const pageTitleKeys: Record<string, string> = {
  "/dashboard": "dashboard",
  "/dashboard/documents": "documents",
  "/dashboard/chat": "chat",
  "/dashboard/analytics": "analytics",
  "/dashboard/settings": "settings",
};

export function Header() {
  const pathname = usePathname();
  const t = useTranslations("nav");

  const titleKey =
    pageTitleKeys[pathname] ||
    (pathname.startsWith("/dashboard/chat/") ? "chat" : "dashboard");

  return (
    <header className="border-b border-slate-200 bg-white px-6 py-4 flex items-center justify-between">
      <h2 className="text-lg font-semibold text-slate-900">{t(titleKey)}</h2>
      <LanguageToggle />
    </header>
  );
}
