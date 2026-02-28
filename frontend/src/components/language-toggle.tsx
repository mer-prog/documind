"use client";

import { useLocale, useTranslations } from "next-intl";
import { useTransition, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { type Locale, locales, defaultLocale } from "@/i18n/config";

export function LanguageToggle() {
  const currentLocale = useLocale();
  const t = useTranslations("language");
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [locale, setLocale] = useState<Locale>(currentLocale as Locale);

  // Restore from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem("locale") as Locale | null;
    if (saved && locales.includes(saved) && saved !== currentLocale) {
      document.cookie = `locale=${saved};path=/;max-age=31536000;SameSite=Lax`;
      startTransition(() => {
        router.refresh();
      });
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  function switchLocale() {
    const nextLocale: Locale = locale === "ja" ? "en" : "ja";
    setLocale(nextLocale);
    localStorage.setItem("locale", nextLocale);
    document.cookie = `locale=${nextLocale};path=/;max-age=31536000;SameSite=Lax`;
    startTransition(() => {
      router.refresh();
    });
  }

  const isJa = locale === "ja";

  return (
    <button
      onClick={switchLocale}
      disabled={isPending}
      className="relative flex items-center h-[44px] min-w-[44px] px-3 rounded-lg border border-slate-200 bg-white text-sm font-medium transition-all duration-150 hover:bg-slate-50 hover:border-slate-300 disabled:opacity-50"
      title={t("toggle")}
      aria-label={t("toggle")}
    >
      <span
        className={`transition-opacity duration-150 ${isJa ? "opacity-100" : "opacity-0 absolute"}`}
      >
        <span className="mr-1.5">🇯🇵</span>
        <span>{t("ja")}</span>
      </span>
      <span
        className={`transition-opacity duration-150 ${!isJa ? "opacity-100" : "opacity-0 absolute"}`}
      >
        <span className="mr-1.5">🇺🇸</span>
        <span>{t("en")}</span>
      </span>
    </button>
  );
}
