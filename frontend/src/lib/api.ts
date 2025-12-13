import { Temperature } from "@/types/Temperature";
import { Utilization } from "@/types/Utilization";
import { DataStatus } from "@/types/DataStatus";
import { MachineOperation } from "@/types/MachineOperation";
import { MachineProgram } from "@/types/MachineProgram";
import { AlertsDailyCount } from "@/types/AlertsDailyCount";
import { AlertsDetail } from "@/types/AlertsDetail";
import { EnergyConsumption } from "@/types/EnergyConsumption";

// Create a base URL constant
const BASE_URL = process.env.NEXT_PUBLIC_API_URL;


// Gets temperatures for the main page of the dashboard
export async function getTemperatures(date: string, sensorName: string = "TEMPERATURA_BASE"){
    if (!BASE_URL) {
        throw new Error('API URL is not configured. Please check your environment variables.');
    }
    if (!date) {
        throw new Error('Date parameter is required');
    }
    try{ 
        const url = `${BASE_URL}/temperature?target_date=${date}&sensor_name=${sensorName}`;
        
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
        //console.log('DATA:', data) // Returns an array of objects of class Temperature [{}, {}]
        //console.log('DATA[0]:', data[0])
        return data as Temperature[];
    }catch(error){
        console.error("Error fetching temperatures:", error);
        throw new Error(`Failed to fetch temperatures: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
}

// Gets the Machine Utilization (running and idle time)
export async function getMachineUtilization(date:string){
    if (!BASE_URL) {
        throw new Error('API URL is not configured. Please check your environment variables.');
    }
    if (!date) {
        throw new Error('Date parameter is required');
    }
    try{ 
        const url =  `${BASE_URL}/machine_util?target_date=${date}`;
        
        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        })
        // No data exists for the date
        if (response.status === 404){
            return null;
        }

        if(!response.ok){
            console.log(response);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        //console.log('DATA[0]:', data[0])
        return data[0] as Utilization;
    }catch(error){
        console.error("Error fetching utilization data:", error);
        throw new Error(`Failed to fetch utilization data: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
}

// Gets the first and last date of data to set restrictions for the filters.
export async function getDataStatus(){
    if(!BASE_URL){
        throw new Error("BASE URL MISSING")
    }

    try{
        const url = `${BASE_URL}/data_status`;
        const response = await fetch(url, {method:"GET", headers:{"Content-Type":"application/json"}})

        if(response.status == 404){
            return null;
        }
        if(!response.ok){
            console.log(response);
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        return data as DataStatus;



    }catch(error){
        console.error("Error fetching utilization data:", error);
        throw new Error(`Failed to fetch utilization data: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
}

// Get the MACHINE IN OPERATION timeline
export async function getMachineOperations(start:string, end:string){
    if(!BASE_URL){
        throw new Error("API URL not configured");
    }
    if(!start || !end){
        throw new Error("Missing start and end timestamps");
    }

    try{
        // encodeURIComponent URL-encodes special characters in a string safely - in our case: spaces
        const url = `${BASE_URL}/machine_changes?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`;

        const response = await fetch(url, {
            method:'get',
            headers: { 
            'Content-type':'Application/json'
        }
        });
        // No data exists for the date
        if (response.status === 404) {
            return [];
        }

        if (!response.ok) {
            console.log(response);
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log( 'DATA: ', data);
        return data as MachineOperation[];
        

    } catch (error) {
        console.error("Error fetching operation status:", error);
        throw new Error(`Failed to fetch operation status: ${error instanceof Error ? error.message : 'Unknown error'}`);
    };

}

// Gets the machine program data for a given date
export async function getMachinePrograms(date: string): Promise<MachineProgram[]> {
    if (!BASE_URL) {
        throw new Error('API URL is not configured. Please check your environment variables.');
    }
    if (!date) {
        throw new Error('Date parameter is required');
    }

    try {
        const url = `${BASE_URL}/machine_program?target_date=${date}`;

        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        });

        // No data exists for the date
        if (response.status === 404) {
            return [];
        }

        if (!response.ok) {
            console.log(response);
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data as MachineProgram[];
    } catch (error) {
        console.error("Error fetching machine programs:", error);
        throw new Error(`Failed to fetch machine programs: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
}

// Gets the daily alert counts by type for a given date (from aggregated DB)
export async function getAlertsDailyCount(date: string): Promise<AlertsDailyCount[]> {
    if (!BASE_URL) {
        throw new Error('API URL is not configured. Please check your environment variables.');
    }
    if (!date) {
        throw new Error('Date parameter is required');
    }

    try {
        const url = `${BASE_URL}/alerts_daily_count?target_date=${date}`;

        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        });

        // No data exists for the date
        if (response.status === 404) {
            return [];
        }

        if (!response.ok) {
            console.log(response);
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data as AlertsDailyCount[];
    } catch (error) {
        console.error("Error fetching alerts daily count:", error);
        throw new Error(`Failed to fetch alerts daily count: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
}

// Gets the detailed alert records for a given date (from aggregated DB)
export async function getAlertsDetail(date: string): Promise<AlertsDetail[]> {
    if (!BASE_URL) {
        throw new Error('API URL is not configured. Please check your environment variables.');
    }
    if (!date) {
        throw new Error('Date parameter is required');
    }

    try {
        const url = `${BASE_URL}/alerts_detail?target_date=${date}`;

        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        });

        // No data exists for the date
        if (response.status === 404) {
            return [];
        }

        if (!response.ok) {
            console.log(response);
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data as AlertsDetail[];
    } catch (error) {
        console.error("Error fetching alerts detail:", error);
        throw new Error(`Failed to fetch alerts detail: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
}

// Gets hourly energy consumption for a given date (from aggregated DB)
export async function getEnergyConsumption(date: string): Promise<EnergyConsumption[]> {
    if (!BASE_URL) {
        throw new Error('API URL is not configured. Please check your environment variables.');
    }
    if (!date) {
        throw new Error('Date parameter is required');
    }

    try {
        const url = `${BASE_URL}/energy_consumption?target_date=${date}`;

        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        });

        // No data exists for the date
        if (response.status === 404) {
            return [];
        }

        if (!response.ok) {
            console.log(response);
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data as EnergyConsumption[];
    } catch (error) {
        console.error("Error fetching energy consumption:", error);
        throw new Error(`Failed to fetch energy consumption: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
}