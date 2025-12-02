import { DemoContainer } from '@mui/x-date-pickers/internals/demo';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { useState } from 'react';
import dayjs from 'dayjs';

export default function BasicDatePicker(date: dayjs.Dayjs | null, setDate: any) {

    
    return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
        <DemoContainer components={['DatePicker']}>
        <DatePicker
        label="Controlled picker"
        value={date}
        onChange={(newValue) => setDate(newValue)}
        />
        </DemoContainer>
    </LocalizationProvider>
    );
    }