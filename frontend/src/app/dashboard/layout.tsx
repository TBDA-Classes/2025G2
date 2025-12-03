// Keeping the interactive parts in client component
'use client';
import type { ReactNode } from "react";
import SideBar from "../components/Sidebar";
import BasicDatePicker from "../components/Datepicker";
import { useSearchParams, useRouter, usePathname } from "next/navigation";


export default function DashboardLayout({children}: { children: ReactNode; }) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const date = searchParams.get('date') || "2022-02-23";

  const handleDateChange = (newDate: string) => {
    router.push(`${pathname}?date=${newDate}`);
  }
  

  return (
    <div className="flex h-screen bg-slate-200 text-slate-100">
      <SideBar />
      <main className="flex-1 overflow-y-auto">
        {/* Sticky Date Selector */}
        <div className="bg-white sticky top-0 z-10">
          <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
            <BasicDatePicker date={date} setDate={handleDateChange}></BasicDatePicker>
          </div>
        </div>
        {children}
      </main>
    </div>
  );
}
