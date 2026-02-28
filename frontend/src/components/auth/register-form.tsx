"use client";

import { useState } from "react";
import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function RegisterForm() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [errorKey, setErrorKey] = useState("");
  const [errorDetail, setErrorDetail] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const t = useTranslations("auth");
  const tc = useTranslations("common");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErrorKey("");
    setErrorDetail("");

    if (password !== confirmPassword) {
      setErrorKey("passwordsNoMatch");
      return;
    }

    if (password.length < 8) {
      setErrorKey("passwordTooShort");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password }),
      });

      if (!res.ok) {
        const data = await res.json();
        setErrorDetail(data.detail || "");
        if (!data.detail) setErrorKey("registrationFailed");
        return;
      }

      // Auto sign in
      const result = await signIn("credentials", {
        email,
        password,
        redirect: false,
      });

      if (result?.error) {
        setErrorKey("registrationSignInFailed");
      } else {
        router.push("/dashboard");
        router.refresh();
      }
    } catch {
      setErrorKey("_common_error");
    } finally {
      setLoading(false);
    }
  }

  const errorMessage = errorDetail || (errorKey === "_common_error" ? tc("error") : errorKey ? t(errorKey) : "");

  return (
    <Card>
      <CardHeader className="text-center">
        <CardTitle className="text-2xl">
          <span className="text-primary">{tc("appName")}</span>
        </CardTitle>
        <CardDescription>{t("createAccountTitle")}</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">{t("name")}</Label>
            <Input
              id="name"
              type="text"
              placeholder={t("namePlaceholder")}
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">{t("email")}</Label>
            <Input
              id="email"
              type="email"
              placeholder={t("emailPlaceholder")}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">{t("password")}</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="confirmPassword">{t("confirmPassword")}</Label>
            <Input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </div>
          {errorMessage && (
            <p className="text-sm text-red-600">{errorMessage}</p>
          )}
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? t("creatingAccount") : t("createAccount")}
          </Button>
          <p className="text-center text-sm text-muted-foreground">
            {t("hasAccount")}{" "}
            <Link href="/login" className="text-primary hover:underline">
              {t("signIn")}
            </Link>
          </p>
        </form>
      </CardContent>
    </Card>
  );
}
