import { DemoContainer } from '@mui/x-date-pickers/internals/demo';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { useState } from 'react';

export default function BasicDatePicker(value) {

    [value, setValue] = useState(date)

    return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
        <DemoContainer components={['DatePicker']}>
        <DatePicker
        label="Controlled picker"
        value={date}
        onChange={(newValue) => setValue(newValue)}
        />
        </DemoContainer>
    </LocalizationProvider>
    );
    }