// Keeping the interactive parts in client component
'use client';
import { useEffect, useState, type ReactNode } from "react";
import SideBar from "../components/Sidebar";
import BasicDatePicker from "../components/Datepicker";
import { useSearchParams, useRouter, usePathname } from "next/navigation";
import { getDataStatus } from "@/lib/api";


export default function DashboardLayout({children}: { children: ReactNode; }) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const [dateRange, setDateRange] = useState<{min: string, max: string} | null>(null);

  // useEffects lets us run side effects after the component renders
  // runs once after mount.
  useEffect(() => {
    getDataStatus().then((status) => {
      if (status){ 
        setDateRange({
          min: status.first_date, 
          max:status.last_date
        });
      }
    });
  }, []);

  const date = searchParams.get('date') || "2022-02-23";

  const date_status = getDataStatus();

  const handleDateChange = (newDate: string) => {
    router.push(`${pathname}?date=${newDate}`, { scroll: false });
  }
  

  return (
    <div className="flex h-screen bg-slate-200">
      <SideBar />
      <main className="flex-1 overflow-y-auto">
        {/* Sticky Date Selector */}
        <div className="bg-white sticky top-0 z-10">
          <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
            <BasicDatePicker 
            date={date} 
            setDate={handleDateChange}
            minDate={dateRange?.min}
            maxDate={dateRange?.max}></BasicDatePicker>
          </div>
        </div>
        {children}
      </main>
    </div>
  );
}
