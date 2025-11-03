// 'use client' // This is necessary for the responsive component to work
'use client'
import { DateState } from '@/types/DateState';
import { ResponsiveBar } from '@nivo/bar'

  const BarChart = ({ _data }: { _data: DateState }) => {
    const chartData = [
      {
        idle: _data.state_idle,
        active: _data.state_active,
        running: _data.state_running
      }
    ];
    
    const keys = ['idle', 'active', 'running'];

    return (
      <ResponsiveBar
          data={chartData}
          keys={keys}
          indexBy="state"
          margin={{ top: 50, right: 60, bottom: 50, left: 60 }}
          padding={0.15}
          layout="vertical"
          colors={{ scheme: 'red_blue' }}
          borderColor={{ from: 'color', modifiers: [['darker', 1.6]] }}
          axisTop={{}}
          axisBottom={{ legend: 'day', legendOffset: 36 }}
          axisLeft={{ legend: 'hours of use', legendOffset: -40 }}
          enableGridX={true}
          enableGridY={false}
          labelSkipWidth={12}
          labelSkipHeight={12}
          labelTextColor={{ from: 'color', modifiers: [['darker', 1.6]] }}
      />
    );
  };

export default BarChart;
