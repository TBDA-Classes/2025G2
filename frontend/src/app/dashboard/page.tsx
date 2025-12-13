import { getTemperatures, getMachineUtilization, getMachinePrograms } from "@/lib/api";
import BoxPlot from "../components/BoxPlot";
import TimelineSection from "../components/TimelineSection";

// Colors for program badges - cycling through these
const PROGRAM_COLORS = [
  { bg: 'bg-blue-500', border: 'border-blue-400', text: 'text-blue-500' },
  { bg: 'bg-purple-500', border: 'border-purple-400', text: 'text-purple-500' },
  { bg: 'bg-pink-500', border: 'border-pink-400', text: 'text-pink-500' },
  { bg: 'bg-orange-400', border: 'border-orange-300', text: 'text-orange-500' },
  { bg: 'bg-emerald-500', border: 'border-emerald-400', text: 'text-emerald-500' },
  { bg: 'bg-cyan-500', border: 'border-cyan-400', text: 'text-cyan-500' },
  { bg: 'bg-amber-500', border: 'border-amber-400', text: 'text-amber-500' },
  { bg: 'bg-rose-500', border: 'border-rose-400', text: 'text-rose-500' },
];

export default async function Dashboard({
  searchParams // page components automatically receive these props
} : {
  searchParams: Promise<{date?: string}>
}) {

  try {
    const params = await searchParams;
    console.log("Dashboard received date param:", params);
    const date = params.date || "2021-09-14";
    const temperature_data = await getTemperatures(date);
    const machine_util_data = await getMachineUtilization(date);
    const program_data = await getMachinePrograms(date);

    // Calculate program statistics
    const totalPrograms = program_data.length;
    const totalSeconds = program_data.reduce((sum, p) => sum + p.duration_seconds, 0);
    const totalHours = Math.floor(totalSeconds / 3600);
    const totalMinutes = Math.floor((totalSeconds % 3600) / 60);


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

        {/* Machine Status Timeline Section - Client Component for dynamic time selection */}
        <TimelineSection date={date} />

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
              Program Statistics (24 Hours)
            </h2>
            
            {program_data.length > 0 ? (
              <>
                {/* Program Cards Grid */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
                  {program_data.map((program, index) => {
                    const color = PROGRAM_COLORS[index % PROGRAM_COLORS.length];
                    const minutes = Math.round(program.duration_seconds / 60);
                    const displayMinutes = program.duration_seconds > 0 && minutes === 0 ? '<1' : minutes;
                    return (
                      /* the key attribute is for identifiying the items during rendering */
                      <div 
                        key={program.program} 
                        className={`border-2 ${color.border} rounded-xl p-4 hover:shadow-md transition-shadow`}
                      >
                        <div className="flex items-center gap-2 mb-2">
                          <span className={`${color.bg} text-white text-sm font-bold px-2 py-1 rounded-md`}>
                            P{program.program}
                          </span>
                        </div>
                        <p className="text-slate-600 text-sm">{displayMinutes} min</p>
                      </div>
                    );
                  })}
                </div>

                {/* Summary Row */}
                <div className="border-t border-slate-200 pt-4">
                  <div className="grid grid-cols-3 text-center">
                    <div>
                      <p className="text-slate-500 text-sm">Programs</p>
                      <p className="text-xl font-bold text-slate-800">{totalPrograms}</p>
                    </div>
                    <div>
                      <p className="text-slate-500 text-sm">Total Time</p>
                      <p className="text-xl font-bold text-slate-800">{totalHours}h {totalMinutes}min</p>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <p className="text-red-600">No program data available for {date}</p>
            )}
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
                <div className="bg-green-600 h-2 rounded-full" style={{ width: `${machine_util_data?.running_percentage ?? '100'}%`}}></div>
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
                <div className="bg-red-600 h-2 rounded-full" style={{ width: `${machine_util_data?.down_percentage ?? '100'}%` }}></div>
              </div>
              <p className="text-slate-600 text-sm"> {machine_util_data?.state_planned_down ?? 'N/A'} / 24 hours</p>
            </div>
          </div>

          {/* Total */}
          <p className="text-center text-slate-500 text-sm">
            Total: {machine_util_data ? machine_util_data.state_planned_down + machine_util_data.state_running : 24} hours
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
