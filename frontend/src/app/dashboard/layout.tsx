// app/dashboard/layout.tsx
import type { ReactNode } from "react";
import SideBar from "../components/Sidebar";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen bg-slate-200 text-slate-100">
      <SideBar />
      <main className="flex-1 p-8">
        {children}
      </main>
    </div>
  );
}
