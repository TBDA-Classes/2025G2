'use client'
import { ResponsiveCalendar } from '@nivo/calendar'
import { useRouter } from 'next/navigation';


const data = [
    {
      "value": 398,
      "day": "2021-01-07"
    },
    {
      "value": 245,
      "day": "2021-01-08"
    },
    {
      "value": 320,
      "day": "2021-01-09"
    },
    {
      "value": 180,
      "day": "2021-01-12"
    },
    {
      "value": 380,
      "day": "2021-01-10"
    },
    {
      "value": 239,
      "day": "2021-01-11"
    },
    {
      "value": 283,
      "day": "2021-01-13"
    },
    {
      "value": 308,
      "day": "2021-01-14"
    },
    {
      "value": 193,
      "day": "2021-01-15"
    },
    {
      "value": 304,
      "day": "2021-01-16"
    },
    {
      "value": 275,
      "day": "2021-01-18"
    },
    {
      "value": 310,
      "day": "2021-01-19"
    },
    {
      "value": 195,
      "day": "2021-01-20"
    },
    {
      "value": 340,
      "day": "2021-01-21"
    },
    {
      "value": 267,
      "day": "2021-01-22"
    },
    {
      "value": 289,
      "day": "2021-01-25"
    },
    {
      "value": 315,
      "day": "2021-01-26"
    },
    {
      "value": 220,
      "day": "2021-01-27"
    },
    {
      "value": 298,
      "day": "2021-01-28"
    },
    {
      "value": 285,
      "day": "2021-01-29"
    },
    {
      "value": 325,
      "day": "2021-02-01"
    },
    {
      "value": 290,
      "day": "2021-02-02"
    },
    {
      "value": 312,
      "day": "2021-02-03"
    },
    {
      "value": 268,
      "day": "2021-02-04"
    },
    {
      "value": 295,
      "day": "2021-02-05"
    },
  ]



const MyCalendar = ({ data } : { data:any[]}) => {
    const router = useRouter();

    return(
    <ResponsiveCalendar
        data={data}
        from="2021-01-07"
        to="2021-02-07"
        emptyColor="#eeeeee"
        margin={{ top: 40, right: 40, bottom: 40, left: 40 }}
        yearSpacing={40}
        monthBorderColor="#ffffff"
        dayBorderWidth={2}
        dayBorderColor="#ffffff"
        onClick = {(day) => {
            router.push(`/dashboard/${day.day}`);
        }}
        legends={[
            {
                anchor: 'bottom-right',
                direction: 'row',
                translateY: 36,
                itemCount: 4,
                itemWidth: 42,
                itemHeight: 36,
                itemsSpacing: 14,
                itemDirection: 'right-to-left'
            }
        ]}
    />
)};

export default function DashboardCalendar(){
    return(
        <div style={{width:'100%', height:'600px'}}>
            <MyCalendar data={data} />
        </div>
    )
}
