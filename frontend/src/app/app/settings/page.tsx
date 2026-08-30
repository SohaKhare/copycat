import type { Metadata } from "next";
import { PageHeader } from "@/components/app/PageHeader";
import { PrivacySettingsCard } from "@/components/settings/PrivacySettingsCard";

export const metadata: Metadata = {
  title: "Settings",
};

export default function SettingsPage() {
  return (
    <>
      <PageHeader title="Settings" />
      <div className="flex flex-col gap-6">
        <PrivacySettingsCard />
      </div>
    </>
  );
}
