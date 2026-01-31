'use client';

import React from 'react';

interface CarbonLimitMeterProps {
    percentage: number;
    current: number;
    limit: number;
}

export default function CarbonLimitMeter({ percentage, current, limit }: CarbonLimitMeterProps) {
    const getColor = () => {
        if (percentage <= 70) return 'text-status-safe';
        if (percentage <= 100) return 'text-status-warning';
        return 'text-status-exceeded';
    };

    const getStrokeColor = () => {
        if (percentage <= 70) return '#10b981';
        if (percentage <= 100) return '#fbbf24';
        return '#ef4444';
    };

    const radius = 80;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (Math.min(percentage, 100) / 100) * circumference;

    return (
        <div className="glass-card p-8 flex flex-col items-center">
            <h3 className="text-xl font-semibold mb-6">Carbon Budget Usage</h3>

            <div className="relative">
                <svg width="200" height="200" className="transform -rotate-90">
                    {/* Background circle */}
                    <circle
                        cx="100"
                        cy="100"
                        r={radius}
                        fill="none"
                        stroke="#1e2330"
                        strokeWidth="12"
                    />

                    {/* Progress circle */}
                    <circle
                        cx="100"
                        cy="100"
                        r={radius}
                        fill="none"
                        stroke={getStrokeColor()}
                        strokeWidth="12"
                        strokeLinecap="round"
                        strokeDasharray={circumference}
                        strokeDashoffset={strokeDashoffset}
                        className="transition-all duration-1000"
                    />
                </svg>

                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className={`text-4xl font-bold ${getColor()}`}>
                        {percentage.toFixed(1)}%
                    </span>
                    <span className="text-gray-500 text-sm mt-1">used</span>
                </div>
            </div>

            <div className="mt-6 text-center">
                <div className="text-gray-400 text-sm">
                    {current.toFixed(2)} / {limit.toFixed(2)} kg CO₂
                </div>
                <div className="text-gray-500 text-xs mt-1">
                    {(limit - current).toFixed(2)} kg remaining
                </div>
            </div>
        </div>
    );
}
