"use client";
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { useState, useEffect } from 'react';
import dayjs from 'dayjs';


// Important fix: JSX components needs their attributes passed as a single props object {}.
export default function BasicDatePicker({
    date, setDate, minDate, maxDate
} : {
    date: string, setDate : any, minDate : string | undefined, maxDate: string | undefined}) {

    // Fix hydration mismatch: only render DatePicker on client
    const [mounted, setMounted] = useState(false);
    useEffect(() => {
        setMounted(true);
    }, []);

    // Show placeholder during SSR to avoid hydration mismatch
    if (!mounted) {
        return (
            <div className="h-14 w-56 bg-slate-100 rounded animate-pulse" />
        );
    }
    
    return (
        <LocalizationProvider dateAdapter={AdapterDayjs}>
            <DatePicker
            label="Select date"
            value={dayjs(date)}
            minDate={minDate ? dayjs(minDate) : undefined}
            maxDate={maxDate ? dayjs(maxDate) : undefined}
            onChange={(newValue) => {
                setDate(newValue?.format('YYYY-MM-DD') || '')
            }}
            />
        </LocalizationProvider>
    );
}