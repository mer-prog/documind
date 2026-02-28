"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { signOut, useSession } from "next-auth/react";
import { useTranslations } from "next-intl";
import { clearTokenCache } from "@/lib/api-client";
import {
  BarChart3,
  FileText,
  Home,
  LogOut,
  MessageSquare,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";

const navItems = [
  { href: "/dashboard", labelKey: "dashboard" as const, icon: Home },
  { href: "/dashboard/documents", labelKey: "documents" as const, icon: FileText },
  { href: "/dashboard/chat", labelKey: "chat" as const, icon: MessageSquare },
  { href: "/dashboard/analytics", labelKey: "analytics" as const, icon: BarChart3 },
  { href: "/dashboard/settings", labelKey: "settings" as const, icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { data: session } = useSession();
  const t = useTranslations("common");
  const tNav = useTranslations("nav");

  return (
    <div className="flex flex-col h-full w-[280px] border-r border-slate-200 bg-white">
      <div className="p-6">
        <h1 className="text-xl font-bold text-primary">{t("appName")}</h1>
        <p className="text-xs text-muted-foreground mt-1">
          {t("appTagline")}
        </p>
      </div>

      <Separator />

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const isActive =
            item.href === "/dashboard"
              ? pathname === "/dashboard"
              : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
                isActive
                  ? "bg-primary-50 text-primary font-medium"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              )}
            >
              <item.icon className="h-4 w-4" />
              {tNav(item.labelKey)}
            </Link>
          );
        })}
      </nav>

      <Separator />

      <div className="p-4">
        <div className="flex items-center gap-3 mb-3">
          <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center text-primary text-sm font-medium">
            {session?.user?.name?.[0]?.toUpperCase() || "U"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">
              {session?.user?.name || t("user")}
            </p>
            <p className="text-xs text-muted-foreground truncate">
              {session?.user?.email || ""}
            </p>
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="w-full justify-start text-muted-foreground"
          onClick={() => {
            clearTokenCache();
            signOut({ callbackUrl: "/login" });
          }}
        >
          <LogOut className="h-4 w-4 mr-2" />
          {t("signOut")}
        </Button>
      </div>
    </div>
  );
}
