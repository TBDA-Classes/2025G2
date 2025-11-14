
import TimelineChart from "../components/TimelineChart";
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

export default async function Dashboard() {
  try {
    return (
      <div>
        {/* Sticky Date Selector */}
        <div className="bg-white">
        <div className="sticky top-0 z-10 bg-white rounded-lg shadow-sm p-4 mb-6">
          <p className="text-slate-800 font-medium">
            Saturday, February 19, 2022
          </p>
        </div>
        </div>

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
        </div>
      </div>
    );
  } catch (error) {
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
