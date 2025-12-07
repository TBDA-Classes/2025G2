import { getTemperatures, getMachineUtilization } from "@/lib/api";

import TimelineChart from "../components/TimelineChart";
import BoxPlot from "../components/BoxPlot";

const data = [
  {
    "country": "AD",
    "hot dog": 51,
    "burger": 12,
    "sandwich": 132,
    "kebab": 26,
    "fries": 112,
    "donut": 51
  }
];

export default async function Dashboard({
  searchParams // page components automatically receive these props
} : {
  searchParams: Promise<{date?: string}>
}) {

  try {
    const params = await searchParams;
    console.log("Dashboard received date param:", params);
    const date = params.date || "2022-02-23";
    const temperature_data = await getTemperatures(date);
    const machine_util_data = await getMachineUtilization(date);


    return (
      
      <div className="p-8"> {/* Must be used for all children containers*/}
      
        {/* Main Content */}
        <div className="space-y-6">

        {/* Page Header */}
        <div>
          <h1 className="text-4xl font-bold text-slate-900 mb-2">
            Production Dashboard
          </h1>
          <p className="text-slate-600 text-lg">
            Monitoring of CNC machine
          </p>
        </div>

        {/* Machine Status Timeline Section */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          {/* Section Header */}
          <h2 className="text-2xl font-semibold text-slate-900 mb-4">
            Machine Status Timeline (24 Hours)
          </h2>

          {/* Legend */}
          <div className="flex gap-6 mb-4">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-green-500"></div>
              <span className="text-slate-700 font-medium">RUN</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
              <span className="text-slate-700 font-medium">IDLE</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-red-500"></div>
              <span className="text-slate-700 font-medium">DOWN</span>
            </div>
          </div>

          {/* Timeline Chart */}
          <div className="h-[400px]">
            <TimelineChart data={data} />
          </div>
        </div>

        <div className="flex flex-row gap-10 ">
          <div className="bg-white rounded-lg shadow-sm p-6 w-1/2">
            <h2 className="text-2xl font-semibold text-slate-900 mb-4">
            Temperature History (24 Hours)
            </h2>
            <div className="h-[400px]">
              {temperature_data.length > 0 ? (
              <BoxPlot data={temperature_data} />
              ):(
              <p className="text-red-600">
              No temperature data available for {date}</p>
              )}
            
          </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-6 w-1/2">
            <h2 className="text-2xl font-semibold text-slate-900 mb-4">
            Program History (24 Hours)
            </h2>
            <div className="h-[400px]">
            <TimelineChart data={data} />
          </div>
          </div>
        </div>

        {/* Machine Utilization Section */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-2xl font-semibold text-slate-900 mb-2">
            Machine Utilization
          </h2>
          <p className="text-slate-600 mb-6">
            Machine Status Distribution (24h)
          </p>

          {/* Status Cards */}
          <div className="grid grid-cols-3 gap-6 mb-4">
            {/* Running Time Card */}
            <div className="bg-green-50 rounded-lg p-6">
              <div className="flex justify-between items-baseline mb-3">
                <span className="text-slate-700 font-medium">Running Time</span>
                <span className="text-3xl font-bold text-green-600">{machine_util_data?.running_percentage ?? 'N/A'}%</span>
              </div>
              <div className="w-full bg-green-200 rounded-full h-2 mb-2">
                <div className="bg-green-600 h-2 rounded-full" style={{ width: '84.4%' }}></div>
              </div>
              <p className="text-slate-600 text-sm"> {machine_util_data?.state_running ?? 'N/A'} / 24 hours</p>
            </div>

            {/* Idle Time Card */}
            <div className="bg-yellow-50 rounded-lg p-6">
              <div className="flex justify-between items-baseline mb-3">
                <span className="text-slate-700 font-medium">Idle Time</span>
                <span className="text-3xl font-bold text-yellow-600">N/A</span>
              </div>
              <div className="w-full bg-yellow-200 rounded-full h-2 mb-2">
                <div className="bg-yellow-600 h-2 rounded-full" style={{ width: '0%' }}></div>
              </div>
              <p className="text-slate-600 text-sm">N/A</p>
            </div>

            {/* Down Time Card */}
            <div className="bg-red-50 rounded-lg p-6">
              <div className="flex justify-between items-baseline mb-3">
                <span className="text-slate-700 font-medium">Down Time</span>
                <span className="text-3xl font-bold text-red-600">{machine_util_data?.down_percentage ?? 'N/A'}%</span>
              </div>
              <div className="w-full bg-red-200 rounded-full h-2 mb-2">
                <div className="bg-red-600 h-2 rounded-full" style={{ width: '5.2%' }}></div>
              </div>
              <p className="text-slate-600 text-sm"> {machine_util_data?.state_planned_down ?? 'N/A'} / 24 hours</p>
            </div>
          </div>

          {/* Total */}
          <p className="text-center text-slate-500 text-sm">
            Total: 1440 min (100.0%)
          </p>
        </div>
        </div>
      </div>
    );
  } catch (error) {
    console.log(error);
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h1 className="text-2xl font-bold text-red-800 mb-2">Error</h1>
        <p className="text-red-600">
          Failed to load dashboard data. Make sure the backend is running and the API is accessible.
        </p>
      </div>
    );
  }
}
