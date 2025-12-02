"use client";
import { DemoContainer } from '@mui/x-date-pickers/internals/demo';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { useState } from 'react';
import { useRouter } from "next/navigation";
import dayjs from 'dayjs';


// Important fix: JSX components needs their attributes passed as a single props object {}.
export default function BasicDatePicker({currentDate} : {currentDate: string}) {
    const router = useRouter();

    
    return (
        <LocalizationProvider dateAdapter={AdapterDayjs}>
            <DatePicker
            label="Select date"
            value={dayjs(currentDate)}
            onChange={(newValue) => {
                if (newValue) {
                    router.push(`/dashboard?date=${newValue.format('YYYY-MM-DD')}`);
                }
            }}
            />
        </LocalizationProvider>
    );
    }