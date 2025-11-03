import { Period } from "@/types/Period";
import { DateState } from "@/types/DateState";

// Create a base URL constant
const BASE_URL = process.env.NEXT_PUBLIC_API_URL;

export async function getPeriods(): Promise<Period[]>{
    try {
    // Construct full URL
    const url = `${BASE_URL}/periods`;
    const response = await fetch(url, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        },
    });
    if(!response.ok){
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data as Period[];
    } catch(error){
        console.error("Error fetching periods:", error);
        throw new Error(`Failed to fetch periods: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
}

export async function getDateState(date: string){
    if (!BASE_URL) {
        throw new Error('API URL is not configured. Please check your environment variables.');
    }
    if (!date) {
        throw new Error('Date parameter is required');
    }

    try {
    const url = `${BASE_URL}/machine_activity?target_date=${date}`;
    console.log('Fetching machine activity:', url);
    
    const response = await fetch(url, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        },
    });
        if(!response.ok){
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data[0] as DateState;
    } catch(error){
        console.error("Error fetching date state:", error);
        throw new Error(`Failed to fetch date state: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
}