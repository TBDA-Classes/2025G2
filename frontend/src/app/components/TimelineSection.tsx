'use client';

import { useState, useEffect } from 'react';
import TimelineChart from './TimelineChart';
import { getMachineOperations } from '@/lib/api';
import { MachineOperation } from '@/types/MachineOperation';

interface TimelineSectionProps {
  date: string; // e.g. "2022-02-23"
}

export default function TimelineSection({ date }: TimelineSectionProps) {
  const [startTime, setStartTime] = useState('16:00');
  const [operationData, setOperationData] = useState<MachineOperation[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Calculate end time (30 minutes after start)
  const calculateEndTime = (start: string): string => {
    const [hours, minutes] = start.split(':').map(Number);
    const totalMinutes = hours * 60 + minutes + 30;
    const endHours = Math.floor(totalMinutes / 60) % 24;
    const endMinutes = totalMinutes % 60;
    return `${endHours.toString().padStart(2, '0')}:${endMinutes.toString().padStart(2, '0')}`;
  };

  const endTime = calculateEndTime(startTime);

  // Format times for API call (with date and timezone)
  const timelineStart = `${date} ${startTime}:00+00:00`;
  const timelineEnd = `${date} ${endTime}:00+00:00`;

  // Fetch data when startTime or date changes
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const data = await getMachineOperations(timelineStart, timelineEnd);
        setOperationData(data);
      } catch (error) {
        console.error('Failed to fetch operation data:', error);
        setOperationData([]);
      }
      setIsLoading(false);
    };

    fetchData();
  }, [timelineStart, timelineEnd]);

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      {/* Section Header with Time Picker */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold text-slate-900">
          Machine Operational Timeline
        </h2>
        
        {/* Time Picker */}
        <div className="flex items-center gap-3">
          <label htmlFor="startTime" className="text-slate-600 text-sm">
            Start Time:
          </label>
          <input
            type="time"
            id="startTime"
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
            className="border border-slate-300 rounded-lg px-3 py-2 text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <span className="text-slate-400">to</span>
          <span className="text-slate-600 text-sm bg-slate-100 px-3 py-2 rounded-lg">
            {endTime} (+30 min)
          </span>
        </div>
      </div>

      {/* Legend */}
      <div className="flex gap-6 mb-4">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-green-500"></div>
          <span className="text-slate-700 font-medium">RUN (255)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-red-500"></div>
          <span className="text-slate-700 font-medium">IDLE (0)</span>
        </div>
      </div>

      {/* Timeline Chart */}
      <div className="h-24">
        {isLoading ? (
          <div className="flex items-center justify-center h-full text-slate-500">
            Loading...
          </div>
        ) : operationData.length > 0 ? (
          <TimelineChart data={operationData} startTime={timelineStart} endTime={timelineEnd} />
        ) : (
          <div className="flex items-center justify-center h-full text-slate-500">
            No data available for this time range
          </div>
        )}
      </div>
    </div>
  );
}

