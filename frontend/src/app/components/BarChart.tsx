'use client'
import { DateState } from '@/types/DateState';
import { ResponsiveBar } from '@nivo/bar'

  const BarChart = ({ _data }: { _data: DateState }) => {
    const chartData = [
      {
        day: _data.date,  // Use the date as the index
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
          indexBy="day"
          margin={{ top: 50, right: 130, bottom: 50, left: 60 }}
          padding={0.3}
          layout="vertical"
          colors={{ scheme: 'red_blue' }}
          borderColor={{ from: 'color', modifiers: [['darker', 1.6]] }}
          axisTop={null}  
          axisBottom={{ 
            legend: 'Date', 
            legendOffset: 36,
            legendPosition: 'middle'
          }}
          axisLeft={{ 
            legend: 'Hours of Use', 
            legendOffset: -40,
            legendPosition: 'middle'
          }}
          enableGridX={false}
          enableGridY={true}
          labelSkipWidth={12}
          labelSkipHeight={12}
          labelTextColor={{ from: 'color', modifiers: [['darker', 1.6]] }}
          legends={[
            {
              dataFrom: 'keys',
              anchor: 'bottom-right',
              direction: 'column',
              justify: false,
              translateX: 120,
              translateY: 0,
              itemsSpacing: 2,
              itemWidth: 100,
              itemHeight: 20,
              itemDirection: 'left-to-right',
              itemOpacity: 0.85,
              symbolSize: 20,
            }
          ]}
      />
    );
  };

export default BarChart;
