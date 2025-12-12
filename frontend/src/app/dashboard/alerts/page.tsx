import { getAlertsDailyCount, getAlertsDetail } from "@/lib/api";
import AlertListWithDetails from "../../components/AlertListWithDetails";

export default async function Alerts({
  searchParams
}: {
  searchParams: Promise<{ date?: string }>;
}) {
  try {
    const params = await searchParams;
    const date = params.date || "2021-09-14";
    const alertCounts = await getAlertsDailyCount(date);
    const alertDetails = await getAlertsDetail(date);

    // Helper function to get alert count by type (types are lowercase from agg DB)
    const getAlertCount = (type: string): number => {
      const alert = alertCounts.find((a) => a.alert_type === type);
      return alert?.amount ?? 0;
    };

    const emergencyCount = getAlertCount("emergency");
    const errorCount = getAlertCount("error");
    const warningCount = getAlertCount("warning");
    const otherCount = getAlertCount("other");

    return (
      <div className="p-8">
        <div className="space-y-6">
          {/* Page Header */}
          <div>
            <h1 className="text-2xl font-bold text-slate-900 mb-2">Alert manager</h1>
            <p className="text-slate-600 text-sm">
              Monitor and manage machine alerts
            </p>
          </div>

          <div className="flex gap-6">
            {/* Alert Summary Box */}
            <div className="w-2/3 bg-white rounded-2xl p-6">
              <h2 className="text-1xl font-medium text-slate-800 mb-6">
                Alerts on {new Date(date).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
              </h2>
              {alertCounts.length > 0 ? (
                <div className="flex items-center justify-between">
                  
                  <div className="flex gap-3">
                    <span className="border-2 border-red-400 text-red-500 rounded-full px-4 py-1">
                      {emergencyCount} Emergency
                    </span>
                    <span className="border-2 border-yellow-400 text-yellow-600 rounded-full px-4 py-1">
                      {errorCount} Error
                    </span>
                    <span className="border-2 border-blue-400 text-blue-500 rounded-full px-4 py-1">
                      {warningCount} Warning
                    </span>
                    <span className="border-2 border-slate-400 text-slate-500 rounded-full px-4 py-1">
                      {otherCount} Other
                    </span>
                  </div>
                </div>
              ) : (
                <p className="text-slate-500">No alerts found for {date}</p>
              )}
            </div>
            {/* Empty placeholder to match AlertListWithDetails layout (w-2/3 + gap + w-1/3) */}
            <div className="w-1/3"></div>
          </div>

          {/* Alert List and Details Section - Client Component for interactivity */}
          <AlertListWithDetails alertDetails={alertDetails} date={date} />
        </div>
      </div>
    );
  } catch (error) {
    return (
      <div className="p-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h1 className="text-2xl font-bold text-red-800 mb-2">Error</h1>
          <p className="text-red-600">
            Failed to load alerts data. Make sure the backend is running and the
            API is accessible.
          </p>
        </div>
      </div>
    );
  }
}
