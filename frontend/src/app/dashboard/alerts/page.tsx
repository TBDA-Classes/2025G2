import { getAlertsForDate } from "@/lib/api";
import { Alert } from "@/types/Alert";

export default async function Alerts({
  searchParams
}: {
  searchParams: Promise<{ date?: string }>;
}) {
  try {
    const params = await searchParams;
    const date = params.date || "2022-02-23";
    const alerts = await getAlertsForDate(date);

    // Helper function to get alert count by type
    const getAlertCount = (type: string): number => {
      const alert = alerts.find((a) => a.alert_type === type);
      return alert?.total_occurrences ?? 0;
    };

    const emergencyCount = getAlertCount("Emergency");
    const errorCount = getAlertCount("Error");
    const alertCount = getAlertCount("Alert");
    const otherCount = getAlertCount("Other");

    return (
      <div className="p-8">
        <div className="space-y-6">
          {/* Page Header */}
          <div>
            <h1 className="text-4xl font-bold text-slate-900 mb-2">Alerts</h1>
            <p className="text-slate-600 text-lg">
              Alert summary for {date}
            </p>
          </div>

          <div className="flex gap-6">
            {/* Alert Summary Box */}
            <div className="w-1/2 bg-white rounded-lg p-6">
              <h2 className="text-xl font-semibold text-slate-900 mb-4">
                Alert Summary
              </h2>
              {alerts.length > 0 ? (
                <>
                  <div className="bg-red-400 rounded-lg w-fit p-2 mb-2">
                    {emergencyCount} Emergency
                  </div>
                  <div className="bg-yellow-400 rounded-lg w-fit p-2 mb-2">
                    {errorCount} Error
                  </div>
                  <div className="bg-orange-400 rounded-lg w-fit p-2 mb-2">
                    {alertCount} Alert
                  </div>
                  <div className="bg-blue-400 rounded-lg w-fit p-2">
                    {otherCount} Other
                  </div>
                </>
              ) : (
                <p className="text-slate-500">No alerts found for {date}</p>
              )}
            </div>

            {/* Placeholder for additional content */}
            <div className="w-1/2 bg-white rounded-lg p-6">
              <h2 className="text-xl font-semibold text-slate-900 mb-4">
                Details
              </h2>
              
            </div>
          </div>
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
