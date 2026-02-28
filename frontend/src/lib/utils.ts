import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffSec < 60) return "just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHour < 24) return `${diffHour}h ago`;
  if (diffDay < 7) return `${diffDay}d ago`;
  return date.toLocaleDateString();
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/**
 * Format a date string for chart axis labels using locale-aware formatting.
 * ja: "2/28" style, en: "Feb 28" style
 */
export function formatLocalDate(dateString: string, locale: string): string {
  const date = new Date(dateString);
  if (locale === "ja") {
    return date.toLocaleDateString("ja-JP", {
      month: "numeric",
      day: "numeric",
    });
  }
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

/**
 * Format a full date using locale-aware formatting.
 * ja: "2026/02/28", en: "Feb 28, 2026"
 */
export function formatFullDate(dateString: string, locale: string): string {
  const date = new Date(dateString);
  if (locale === "ja") {
    return date.toLocaleDateString("ja-JP", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    });
  }
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

/**
 * Format currency using locale-aware formatting.
 * ja: "¥1,234", en: "$1,234"
 */
export function formatCurrency(amount: number, locale: string): string {
  if (locale === "ja") {
    return new Intl.NumberFormat("ja-JP", {
      style: "currency",
      currency: "JPY",
      maximumFractionDigits: 0,
    }).format(amount);
  }
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Format a number using locale-aware formatting.
 */
export function formatNumber(num: number, locale: string): string {
  if (locale === "ja") {
    return new Intl.NumberFormat("ja-JP").format(num);
  }
  return new Intl.NumberFormat("en-US").format(num);
}
