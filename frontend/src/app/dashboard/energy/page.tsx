'use client'

import { useSearchParams } from 'next/navigation';
import EnergyChart from '../../components/EnergyChart';

export default function Energy() {
    const searchParams = useSearchParams();
    const date = searchParams.get('date') || "2021-09-14";

    return (
        <div className="space-y-6 p-6">
            <h1 className="text-3xl font-bold text-slate-900">Energy Monitoring</h1>
            
            <EnergyChart date={date} />
        </div>
    );
}
