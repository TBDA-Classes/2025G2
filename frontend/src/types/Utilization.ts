export interface Utilization{
    dt: string;
    state_running: number;
    state_planned_down: number;
    running_percentage: number;
    down_percentage : number;
}