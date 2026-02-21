"use client";

import { usePathname } from "next/navigation";

const pageTitles: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/dashboard/documents": "Documents",
  "/dashboard/chat": "Chat",
  "/dashboard/analytics": "Analytics",
  "/dashboard/settings": "Settings",
};

export function Header() {
  const pathname = usePathname();

  const title =
    pageTitles[pathname] ||
    (pathname.startsWith("/dashboard/chat/") ? "Chat" : "Dashboard");

  return (
    <header className="border-b border-slate-200 bg-white px-6 py-4">
      <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
    </header>
  );
}
