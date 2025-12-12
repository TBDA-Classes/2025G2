'use client';

import { useState, useEffect, useRef } from 'react';
import { AlertsDetail } from '@/types/AlertsDetail';

// Filter options for the dropdown
const FILTER_OPTIONS = [
    { value: 'all', label: 'All' },
    { value: 'emergency', label: 'Emergency' },
    { value: 'error', label: 'Error' }
];

// Helper to get colors based on alert type
const getAlertColors = (type: string) => {
    switch (type) {
        case 'emergency':
            return { border: 'border-red-400', text: 'text-red-500', bg: 'bg-red-50' };
        case 'error':
            return { border: 'border-yellow-400', text: 'text-yellow-600', bg: 'bg-yellow-50' };
        case 'warning':
            return { border: 'border-blue-400', text: 'text-blue-500', bg: 'bg-blue-50' };
        default:
            return { border: 'border-slate-400', text: 'text-slate-500', bg: 'bg-slate-50' };
    }
};

// Helper to format timestamp (removes microseconds)
const formatTimestamp = (dt: string) => {
    // "2021-11-18 00:04:26.265000" -> Split at "." and only pick first part
    return dt.split('.')[0];
};

interface AlertListWithDetailsProps {
    alertDetails: AlertsDetail[];
    date: string;
}

export default function AlertListWithDetails({ alertDetails, date }: AlertListWithDetailsProps) {

    // useState with conditional init
    const [selectedAlert, setSelectedAlert] = useState<AlertsDetail | null>(
    alertDetails.length > 0 ? alertDetails[0] : null
    );

    // Filter state
    const [typeFilter, setTypeFilter] = useState('all');

    // Ref to the scrollable list container
    const listRef = useRef<HTMLDivElement>(null);

    // Filter alerts based on selected type
    const filteredAlerts = typeFilter === 'all' 
        ? alertDetails 
        : alertDetails.filter(alert => alert.alert_type === typeFilter);

    // Scroll to top and select first alert when data or filter changes
    useEffect(() => {
        if (listRef.current) {
            listRef.current.scrollTop = 0;
        }
        setSelectedAlert(filteredAlerts.length > 0 ? filteredAlerts[0] : null);
    }, [alertDetails, typeFilter]);

    return (
    <div className="space-y-4">
        {/* Filter Bar */}
        <div className="bg-white rounded-xl p-4 flex items-center gap-6">
            <div className="flex items-center gap-3">
                <label htmlFor="typeFilter" className="text-slate-600 text-sm font-medium">
                    Type:
                </label>
                <select
                    id="typeFilter"
                    value={typeFilter}
                    onChange={(e) => setTypeFilter(e.target.value)}
                    className="border border-slate-300 rounded-lg px-4 py-2 text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent min-w-[140px]"
                >
                    {FILTER_OPTIONS.map(option => (
                        <option key={option.value} value={option.value}>
                            {option.label}
                        </option>
                    ))}
                </select>
            </div>
            <span className="text-slate-500 text-sm ml-auto">
                {filteredAlerts.length} alert{filteredAlerts.length !== 1 ? 's' : ''}
            </span>
        </div>

        {/* Alert List and Details */}
        <div className="flex gap-6">
            {/* Alert List */}
            <div ref={listRef} className="w-2/3 space-y-3 max-h-[500px] overflow-y-auto">
        {filteredAlerts.length > 0 ? (
            filteredAlerts.map((alert) => {
            const colors = getAlertColors(alert.alert_type);
            const isSelected = selectedAlert?.id === alert.id;
            return (
                <div 
                key={alert.id}
                onClick={() => setSelectedAlert(alert)}
                className={`bg-white rounded-xl p-4 cursor-pointer transition-all ${
                    isSelected 
                    ? `border-2 ${colors.border}` 
                    : 'border border-slate-200 hover:border-slate-300'
                }`}
                >
                <div className="flex items-center gap-3">
                    <svg className={`w-5 h-5 ${colors.text}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                    </svg>
                    <span className={`border-2 ${colors.border} ${colors.text} rounded-full px-3 py-0.5 text-sm`}>
                    {alert.alert_type}
                    </span>
                    {alert.alarm_code && (
                    <span className="text-slate-400 text-sm">{alert.alarm_code}</span>
                    )}
                </div>
                <div className="flex items-center gap-2 mt-2 text-slate-500 text-sm ml-8">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {formatTimestamp(alert.dt)}
                </div>
                {alert.alarm_description && (
                    <p className="mt-2 text-slate-600 text-sm ml-8 truncate">{alert.alarm_description}</p>
                )}
                </div>
            );
            })
        ) : (
            <p className="text-slate-500 p-4">No alerts found{typeFilter !== 'all' ? ` for type "${typeFilter}"` : ` for ${date}`}</p>
        )}
        </div>

        {/* Alert Details Panel */}
        <div className="w-1/3 bg-white rounded-xl p-6">
        <h3 className="text-lg font-semibold text-slate-800 mb-6">Alert Details</h3>
        
        {selectedAlert ? (
            <div className="space-y-5">
            <div>
                <p className="text-slate-400 text-sm mb-1">Type</p>
                <span className={`border-2 ${getAlertColors(selectedAlert.alert_type).border} ${getAlertColors(selectedAlert.alert_type).text} rounded-full px-3 py-0.5 text-sm`}>
                {selectedAlert.alert_type}
                </span>
            </div>

            <div>
                <p className="text-slate-400 text-sm mb-1">Alarm Code</p>
                <p className="text-slate-800 font-medium">{selectedAlert.alarm_code || 'N/A'}</p>
            </div>

            <div>
                <p className="text-slate-400 text-sm mb-1">Description</p>
                <p className="text-slate-800 font-medium">{selectedAlert.alarm_description || 'N/A'}</p>
            </div>

            <div>
                <p className="text-slate-400 text-sm mb-1">Timestamp</p>
                <p className="text-slate-800 font-medium">{formatTimestamp(selectedAlert.dt)}</p>
            </div>
            </div>
        ) : (
            <p className="text-slate-500">Select an alert to view details</p>
        )}
        </div>
        </div>
    </div>
    );
}

