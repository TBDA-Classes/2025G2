


export default async function Energy(){
    try{
        return(
            <div>

            </div>
        )
    }
    catch(error){
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