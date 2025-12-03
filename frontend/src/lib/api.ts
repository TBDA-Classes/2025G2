
import { DateState } from "@/types/DateState";
import { Period } from "@/types/period";
import { METHODS } from "http";
import { Temperature } from "@/types/Temperature";

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


export async function getTemperatures(date:string){
    if (!BASE_URL) {
        throw new Error('API URL is not configured. Please check your environment variables.');
    }
    if (!date) {
        throw new Error('Date parameter is required');
    }
    try{ 
        const url =  `${BASE_URL}/temperature?target_date=${date}`;
        
        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        })
        // No data exists for the date
        if (response.status === 404){
            return [];
        }

        if(!response.ok){
            console.log(response);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('DATA:', data) // Returns an array of objects of class Temperature [{}, {}]
        console.log('DATA[0]:', data[0])
        return data as Temperature[];
    }catch(error){
        console.error("Error fetching temperatures:", error);
        throw new Error(`Failed to fetch temperatures: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
}