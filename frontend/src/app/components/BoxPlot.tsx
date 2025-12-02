"use client"
import { ResponsiveBoxPlot, BoxPlotTooltipProps } from '@nivo/boxplot'
import { Temperature } from '@/types/Temperature'

export default function BoxPlot({ data } : {data :Temperature[]}){

    // Create lookup for readings_count by hour
    const readingsMap = new Map<string, number>();
    
    const boxplotdata = data.flatMap(temp =>{
        const hour = new Date(temp.dt).getHours();
        const group = hour.toString().padStart(2, '0');  
        
        // Store readings count for this hour
        readingsMap.set(group, temp.readings_count);

        const q1 = temp.avg_value - 0.6745 * temp.std_dev;
        const q3 = temp.avg_value + 0.6745 * temp.std_dev;
        return[
            {group, value: temp.min_value},
            {group, value: q1},
            {group, value: temp.avg_value},
            {group, value: q3},
            {group, value: temp.max_value}
        ];
    });

    // Custom tooltip showing only Summary with actual readings count
    const CustomTooltip = ({ label, color, formatted }: BoxPlotTooltipProps) => {
        const readingsCount = readingsMap.get(label) ?? 0;
        return (
            <div style={{ 
                background: 'white', 
                padding: '12px', 
                borderRadius: '4px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
                color: '#333'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ 
                        width: 70, 
                        height: 12, 
                        background: color, 
                        marginRight: 8,
                        borderRadius: 2
                    }} />
                    <strong>{label}</strong>
                </div>
                <div style={{ fontSize: '13px' }}>
                    <div>number of readings: <strong>{readingsCount.toLocaleString()}</strong></div>
                    <div style={{ marginTop: '6px', borderTop: '1px solid #eee', paddingTop: '6px' }}>
                        <div>mean: <strong>{formatted.mean}</strong></div>
                        <div>min: <strong>{formatted.values[0]}</strong></div>
                        <div>max: <strong>{formatted.values[4]}</strong></div>
                    </div>
                </div>
            </div>
        );
    };

    return(
    <ResponsiveBoxPlot
        data={boxplotdata}
        margin={{ top: 60, right: 20, bottom: 60, left: 40 }}
        quantiles={[0, 0.25, 0.5, 0.75, 1]}
        tooltip={CustomTooltip}
        axisBottom={{ legend: 'Time [h]', legendPosition: 'middle', legendOffset: 50 }}
        axisLeft={{ legend: 'Temperature', legendPosition: 'middle', legendOffset: -50 }}
        borderRadius={2}
        colors={{ scheme: 'spectral' }}
        legends={[
            {
                anchor: 'right',
                direction: 'column',
                translateX: 100,
                itemWidth: 60,
                itemHeight: 20,
                itemsSpacing: 3
            }
        ]}
    />
);
}