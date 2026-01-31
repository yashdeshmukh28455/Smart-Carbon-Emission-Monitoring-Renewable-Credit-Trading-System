'use client';

import React from 'react';

interface EmissionGaugeProps {
    title: string;
    value: number;
    unit: string;
    icon: string;
    color: string;
}

export default function EmissionGauge({ title, value, unit, icon, color }: EmissionGaugeProps) {
    return (
        <div className="glass-card p-6 card-hover">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-gray-400 text-sm font-medium">{title}</h3>
                <span className="text-2xl">{icon}</span>
            </div>

            <div className="flex items-baseline gap-2">
                <span className={`text-4xl font-bold ${color}`}>
                    {value.toFixed(2)}
                </span>
                <span className="text-gray-500 text-lg">{unit}</span>
            </div>

            <div className="mt-4 h-2 bg-dark-elevated rounded-full overflow-hidden">
                <div
                    className={`h-full ${color.replace('text-', 'bg-')} transition-all duration-1000`}
                    style={{ width: `${Math.min(100, (value / 50) * 100)}%` }}
                />
            </div>
        </div>
    );
}
