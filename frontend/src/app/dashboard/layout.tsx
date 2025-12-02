// app/dashboard/layout.tsx
"use client"
import type { ReactNode } from "react";
import { useState } from "react";
import dayjs, { Dayjs } from 'dayjs';
import SideBar from "../components/Sidebar";
import BasicDatePicker from "../components/Datepicker";

export default function DashboardLayout({ children }: { children: ReactNode }) {

  // Lifting state up to the layout, this is passed down to children for R & U.
  const [date, setDate] = useState<Dayjs | null>(dayjs('2022-04-17'));

  return (
    <div className="flex h-screen bg-slate-200 text-slate-100">
      <SideBar />
      <main className="flex-1 overflow-y-auto">
        {/* Sticky Date Selector */}
        <div className="bg-white sticky top-0 z-10">
          <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
            <BasicDatePicker 
            date={date} 
            setDate={setDate}>
              
            </BasicDatePicker>
          </div>
        </div>
        {children}
      </main>
    </div>
  );
}
