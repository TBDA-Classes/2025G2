import { DemoContainer } from '@mui/x-date-pickers/internals/demo';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { useState } from 'react';
import dayjs from 'dayjs';

// Important fix: JSX components needs their attributes passed as a single props object {}.
export default function BasicDatePicker({date, setDate} : {date: dayjs.Dayjs | null, setDate: (newDate: dayjs.Dayjs | null) => void}) {

    
    return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
        <DemoContainer components={['DatePicker']}>
        <DatePicker
        label="Controlled picker"
        value={date}
        onChange={(newValue) => setDate(newValue)} // Call parents setter
        />
        </DemoContainer>
    </LocalizationProvider>
    );
    }