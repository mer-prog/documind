import { Sidebar } from "@/components/dashboard/sidebar";
import { Header } from "@/components/dashboard/header";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-auto flex flex-col">
        <Header />
        <div className="flex-1 overflow-auto">{children}</div>
      </main>
    </div>
  );
}
