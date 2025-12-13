'use client'

import { useState, useEffect } from 'react'
import { ResponsiveLine } from '@nivo/line'
import { getEnergyConsumption } from '@/lib/api'
import { EnergyConsumption } from '@/types/EnergyConsumption'

interface EnergyChartProps {
    date: string;
}

interface EnergySummary {
    peakHour: string;
    peakValue: number;
    dailyTotal: number;
}

export default function EnergyChart({ date }: EnergyChartProps) {
    const [chartData, setChartData] = useState<{ id: string; data: { x: string; y: number }[] }[]>([])
    const [summary, setSummary] = useState<EnergySummary | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        async function fetchData() {
            setLoading(true)
            setError(null)
            try {
                const data = await getEnergyConsumption(date)
                
                // Calculate summary stats
                if (data.length > 0) {
                    const peakItem = data.reduce((max, item) => 
                        item.energy_kwh > max.energy_kwh ? item : max, data[0])
                    
                    const dailyTotal = data.reduce((sum, item) => sum + item.energy_kwh, 0)
                    
                    setSummary({
                        peakHour: new Date(peakItem.hour_ts).toLocaleTimeString('en-US', {
                            hour: '2-digit',
                            minute: '2-digit',
                            hour12: false
                        }),
                        peakValue: Math.round(peakItem.energy_kwh * 10) / 10,
                        dailyTotal: Math.round(dailyTotal * 10) / 10  // Total kWh
                    })
                } else {
                    setSummary(null)
                }
                
                // Transform API data to Nivo format
                const nivoData = [{
                    id: "Energy (kWh)",
                    data: data.map((item: EnergyConsumption) => ({
                        x: new Date(item.hour_ts).toLocaleTimeString('en-US', { 
                            hour: '2-digit', 
                            minute: '2-digit',
                            hour12: false 
                        }),
                        y: Math.round(item.energy_kwh * 10) / 10  // Keep 1 decimal
                    }))
                }]
                
                setChartData(nivoData)
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to fetch data')
            } finally {
                setLoading(false)
            }
        }
        
        fetchData()
    }, [date])

    if (loading) {
        return (
            <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white rounded-2xl shadow-sm p-6 animate-pulse">
                        <div className="h-4 bg-slate-200 rounded w-24 mb-4"></div>
                        <div className="h-8 bg-slate-200 rounded w-32"></div>
                    </div>
                    <div className="bg-white rounded-2xl shadow-sm p-6 animate-pulse">
                        <div className="h-4 bg-slate-200 rounded w-24 mb-4"></div>
                        <div className="h-8 bg-slate-200 rounded w-32"></div>
                    </div>
                </div>
                <div className="bg-white rounded-2xl shadow-sm p-6" style={{ height: 400 }}>
                    <h2 className="text-xl font-semibold text-slate-800 mb-4">Hourly Energy Consumption</h2>
                    <div className="flex items-center justify-center h-80 text-slate-500">
                        Loading...
                    </div>
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="bg-white rounded-2xl shadow-sm p-6" style={{ height: 400 }}>
                <h2 className="text-xl font-semibold text-slate-800 mb-4">Hourly Energy Consumption</h2>
                <div className="flex items-center justify-center h-80 text-red-500">
                    {error}
                </div>
            </div>
        )
    }

    if (chartData.length === 0 || chartData[0].data.length === 0) {
        return (
            <div className="bg-white rounded-2xl shadow-sm p-6" style={{ height: 400 }}>
                <h2 className="text-xl font-semibold text-slate-800 mb-4">Hourly Energy Consumption</h2>
                <div className="flex items-center justify-center h-80 text-slate-500">
                    No data available for {date}
                </div>
            </div>
        )
    }

    return (
        <div className="space-y-4">
            {/* Summary Cards */}
            <div className="grid grid-cols-2 gap-4">
                {/* Peak Hour Card */}
                <div className="bg-white rounded-2xl shadow-sm p-6">
                    <div className="flex items-center justify-between">
                        <span className="text-slate-600 text-sm font-medium">Peak Hour</span>
                        
                        <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                            <circle cx="12" cy="12" r="10"/>
                            <path d="M12 6v6l4 2"/>
                        </svg>
                    </div>
                    <div className="mt-2">
                        <span className="text-3xl font-bold text-blue-600">{summary?.peakValue}</span>
                        <span className="text-xl text-blue-600 ml-1">kWh</span>
                    </div>
                    <p className="text-slate-500 text-sm mt-1">at {summary?.peakHour}</p>
                </div>

                {/* Daily Total Card */}
                <div className="bg-white rounded-2xl shadow-sm p-6">
                    <div className="flex items-center justify-between">
                        <span className="text-slate-600 text-sm font-medium">Daily Total</span>
                        <svg className="w-6 h-6 text-amber-500" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M13 3L4 14h7l-2 7 9-11h-7l2-7z"/>
                        </svg>
                    </div>
                    <div className="mt-2">
                        <span className="text-3xl font-bold text-blue-600">{summary?.dailyTotal}</span>
                        <span className="text-xl text-blue-600 ml-1">kWh</span>
                    </div>
                    <p className="text-slate-500 text-sm mt-1">Total energy consumed today</p>
                </div>
            </div>

            {/* Chart */}
            <div className="bg-white rounded-2xl shadow-sm p-6" style={{ height: 400 }}>
                <h2 className="text-xl font-semibold text-slate-800 mb-4">Hourly Energy Consumption</h2>
                <div style={{ height: 320 }}>
                    <ResponsiveLine
                        data={chartData}
                        margin={{ top: 20, right: 30, bottom: 50, left: 60 }}
                        xScale={{ type: 'point' }}
                        yScale={{ 
                            type: 'linear', 
                            min: 0, 
                            max: 'auto',
                            stacked: false, 
                            reverse: false 
                        }}
                        axisTop={null}
                        axisRight={null}
                        axisBottom={{
                            tickSize: 5,
                            tickPadding: 5,
                            tickRotation: 0,
                            legend: '',
                            legendOffset: 36,
                            legendPosition: 'middle'
                        }}
                        axisLeft={{
                            tickSize: 5,
                            tickPadding: 5,
                            tickRotation: 0,
                            legend: 'kWh',
                            legendOffset: -45,
                            legendPosition: 'middle'
                        }}
                        colors={['#4a90d9']}
                        lineWidth={2}
                        pointSize={8}
                        pointColor={{ theme: 'background' }}
                        pointBorderWidth={2}
                        pointBorderColor={{ from: 'seriesColor' }}
                        pointLabelYOffset={-12}
                        enableArea={false}
                        enableGridX={false}
                        enableGridY={true}
                        useMesh={true}
                        enableTouchCrosshair={true}
                        tooltip={({ point }) => (
                            <div className="bg-white px-4 py-3 rounded shadow-lg border border-slate-200 min-w-[140px]">
                                <div className="flex justify-between gap-4">
                                    <span className="text-slate-500">hour:</span>
                                    <span className="text-slate-800 font-medium">{point.data.xFormatted}</span>
                                </div>
                                <div className="flex justify-between gap-4">
                                    <span className="text-slate-500">kWh:</span>
                                    <span className="text-slate-800 font-medium">{point.data.yFormatted}</span>
                                </div>
                            </div>
                        )}
                        theme={{
                            grid: {
                                line: {
                                    stroke: '#e2e8f0',
                                    strokeDasharray: '4 4'
                                }
                            },
                            axis: {
                                ticks: {
                                    text: {
                                        fill: '#64748b',
                                        fontSize: 11
                                    }
                                },
                                legend: {
                                    text: {
                                        fill: '#475569',
                                        fontSize: 12,
                                        fontWeight: 500
                                    }
                                }
                            }
                        }}
                    />
                </div>
            </div>
        </div>
    )
}
