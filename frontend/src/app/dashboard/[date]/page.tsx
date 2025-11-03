import { getDateState } from '@/lib/api';
import BarChart from '../../components/BarChart';

// Mark as Server Component explicitly
export const dynamic = 'force-dynamic';

export default async function Dashboard({ params }: { params: { date: string } }) {
  try {
    if (!params?.date) {
      throw new Error('Date parameter is required');
    }
    
    const dateState = await getDateState(params.date);
    
    if (!dateState) {
      throw new Error('No data returned for this date');
    }

    return (
      <div style={{ height: '600px', width: '100%' }}>
        <BarChart _data={dateState} />
      </div>
    );
  } catch (error) {
    console.error('Dashboard error:', error);
    return <div>Error loading data: {error instanceof Error ? error.message : 'Unknown error'}</div>;
  }
}