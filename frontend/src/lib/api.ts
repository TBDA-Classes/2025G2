import { Period } from "@/types/period";
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