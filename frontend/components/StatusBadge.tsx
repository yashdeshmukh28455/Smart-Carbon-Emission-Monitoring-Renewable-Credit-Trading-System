'use client';

import React from 'react';

interface StatusBadgeProps {
    status: 'safe' | 'warning' | 'exceeded';
    percentage: number;
}

export default function StatusBadge({ status, percentage }: StatusBadgeProps) {
    const getStatusConfig = () => {
        switch (status) {
            case 'safe':
                return {
                    bg: 'bg-status-safe/20',
                    border: 'border-status-safe',
                    text: 'text-status-safe',
                    icon: '✓',
                    label: 'Safe',
                };
            case 'warning':
                return {
                    bg: 'bg-status-warning/20',
                    border: 'border-status-warning',
                    text: 'text-status-warning',
                    icon: '⚠',
                    label: 'Warning',
                };
            case 'exceeded':
                return {
                    bg: 'bg-status-exceeded/20',
                    border: 'border-status-exceeded',
                    text: 'text-status-exceeded',
                    icon: '✕',
                    label: 'Exceeded',
                };
        }
    };

    const config = getStatusConfig();

    return (
        <div className={`status-badge ${config.bg} ${config.border} ${config.text} border-2 ${status === 'exceeded' ? 'animate-pulse-slow' : ''}`}>
            <span className="text-lg">{config.icon}</span>
            <span>{config.label}</span>
            <span className="font-bold">{percentage.toFixed(1)}%</span>
        </div>
    );
}
