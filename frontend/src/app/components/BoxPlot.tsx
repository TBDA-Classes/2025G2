"use client"
import { ResponsiveBoxPlot } from '@nivo/boxplot'
import { Temperature } from '@/types/Temperature'

export default function BoxPlot({ data } : {data :Temperature[]}){

    const boxplotdata = data.map(temp =>{
        // Extract hour
        const hour = new Date(temp.dt).getHours();

        // return group (hour), value, extremes and metadata (readings_count)
        return{
            group: `${hour}:00`,
            min: temp.min_value,
            median: temp.avg_value,
            max: temp.max_value,
            n: temp.readings_count
        };
        

    });
    return(
    <ResponsiveBoxPlot /* or BoxPlot for fixed dimensions */
        data={boxplotdata}
        margin={{ top: 60, right: 140, bottom: 60, left: 60 }}
        minValue={"auto"} 
        maxValue={"auto"} // Temperature range, change once we know standard values

        axisBottom={{ legend: 'Time [h]', legendPosition: 'middle', legendOffset: 50 }}
        axisLeft={{ legend: 'Temperature ', legendPosition: 'middle', legendOffset: -50 }}
        borderRadius={2}
        medianColor={{ from: 'color', modifiers: [['darker', 0.3]] }}
        whiskerColor={{ from: 'color', modifiers: [['darker', 0.3]] }}
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