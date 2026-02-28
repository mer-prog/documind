"use client";

import { useTranslations } from "next-intl";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";

export default function SettingsPage() {
  const t = useTranslations("settings");

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">{t("title")}</h1>

      <Tabs defaultValue="general">
        <TabsList>
          <TabsTrigger value="general">{t("general")}</TabsTrigger>
          <TabsTrigger value="members">{t("members")}</TabsTrigger>
          <TabsTrigger value="api-keys">{t("apiKeys")}</TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="mt-6 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>{t("workspace")}</CardTitle>
              <CardDescription>
                {t("workspaceDescription")}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="workspace-name">{t("workspaceName")}</Label>
                <Input
                  id="workspace-name"
                  placeholder={t("workspacePlaceholder")}
                  disabled
                />
              </div>
              <Button disabled>{t("saveChanges")}</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{t("profile")}</CardTitle>
              <CardDescription>
                {t("profileDescription")}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">{t("profileName")}</Label>
                <Input id="name" placeholder={t("profileNamePlaceholder")} disabled />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">{t("profileEmail")}</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder={t("profileEmailPlaceholder")}
                  disabled
                />
              </div>
              <Button disabled>{t("updateProfile")}</Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="members" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>{t("teamMembers")}</CardTitle>
              <CardDescription>
                {t("teamDescription")}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                {t("teamComingSoon")}
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="api-keys" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>{t("apiKeysTitle")}</CardTitle>
              <CardDescription>
                {t("apiKeysDescription")}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                {t("apiKeysComingSoon")}
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
