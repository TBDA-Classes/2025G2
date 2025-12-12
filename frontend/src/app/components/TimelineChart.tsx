"use client";

import { MachineOperation } from "@/types/MachineOperation";

interface TimeSegment {
  startSeconds: number;
  durationSeconds: number;
  state: 'RUN' | 'IDLE';
}

function transformToSegments(
  operations: MachineOperation[],
  startTime: Date,
  endTime: Date
): TimeSegment[] {
  if (operations.length === 0) 
    return [];

  const segments: TimeSegment[] = [];
  // Copy and using sort comparator (automatic sorting based on the returned sign)
  const sorted = [...operations].sort(
    (a, b) => new Date(a.ts).getTime() - new Date(b.ts).getTime()
  );

  // Seconds from midnight used as reference point
  // Had to move away from this method because of timezone issues etc.
  //const rangeStartSeconds = startTime.getHours() * 60 * 60 + startTime.getMinutes() * 60 + startTime.getSeconds();
  const rangeStartMs = startTime.getTime();
  let tot_duration = 0;
  
  for (let i = 0; i < sorted.length; i++) {
    const current = sorted[i];
    const next = sorted[i + 1];

    // Calculating the seconds from midnight for the current and commingstamp
    
    const currentMs = new Date(current.ts).getTime();
    const nextMs = next ? new Date(next.ts).getTime() : endTime.getTime();

    // Small detour to fill in a segment at the beginning
    if(i === 0 && currentMs != rangeStartMs){
        segments.push({
            startSeconds: 0,
            durationSeconds: (currentMs - rangeStartMs) / 1000,
            state: current.value === 255 ? 'IDLE' : 'RUN'
        });
    }
    
    segments.push({
      startSeconds: (currentMs - rangeStartMs) / 1000,
      durationSeconds: (nextMs - currentMs) / 1000,
      state: current.value === 255 ? 'RUN' : 'IDLE',
    });
    tot_duration += (nextMs - currentMs) / 1000;
  }
  
  if(tot_duration < (endTime.getTime())/1000 - startTime.getTime()){
    segments.unshift({
        startSeconds: rangeStartMs / 1000,
        durationSeconds: ((endTime.getTime())/1000 - startTime.getTime() - tot_duration),
        state: sorted[0].value === 255 ? 'IDLE' : 'RUN',
    });
  }
  
  return segments;
}


interface TimelineChartProps {
  data: MachineOperation[];
  startTime: string;
  endTime: string;
}

const TimelineChart = ({ data, startTime, endTime }: TimelineChartProps) => {
  const start = new Date(startTime);
  const end = new Date(endTime);
  const totalSeconds = (end.getTime() - start.getTime()) / 1000;
  const segments = transformToSegments(data, start, end);
  debugger;
  const formatTime = (date: Date) => {
    // .padStart(2, '0') adds 0's to reach length 2.
    // Using getUTCHours/Minutes since our timestamps are in UTC (+00:00)
    return `${date.getUTCHours().toString().padStart(2, '0')}:${date.getUTCMinutes().toString().padStart(2, '0')}`;
  };

  if (data.length === 0) {
    return <p className="text-slate-500">No operation data available</p>;
  }

  return (
    <div className="w-full">
      {/* Timeline bar */}
      <div className="flex h-12 rounded overflow-hidden border border-slate-200">
        {segments.map((segment, i) => (
          <div
            key={i}
            className={segment.state === 'RUN' ? 'bg-green-500' : 'bg-red-500'}
            style={{ width: `${(segment.durationSeconds / totalSeconds) * 100}%` }}
            title={`${segment.state}: ${segment.durationSeconds} sec`}
          />
        ))}
      </div>

      {/* Time axis labels */}
      <div className="flex justify-between mt-2 text-sm text-slate-600">
        <span>{formatTime(start)}</span>
        <span>{formatTime(end)}</span>
      </div>
    </div>
  );
};

export default TimelineChart;
