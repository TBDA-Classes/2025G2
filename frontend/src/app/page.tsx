import { getPeriods } from "@/lib/api";


export default async function Home() {
  try{
    const periods = await getPeriods();
    return (
      <div>
        <h1>Periods</h1>
        <ul>
          {periods.map((period) => (
            <li key={period.id}>{period.name}</li>
          ))}
        </ul>
      </div>
    );
  } catch (error) {
  return (
    <div>
      <h1>Error</h1>
      <p>Failed to load periods. Make sure the backend is running and the API is accessible.</p>
    </div>
  );
  }
  
}
