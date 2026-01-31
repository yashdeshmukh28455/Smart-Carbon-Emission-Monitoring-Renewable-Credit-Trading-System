'use client';

import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { emissionsAPI } from '@/lib/api';

type Period = 'daily' | 'monthly' | 'yearly';

export default function EmissionChart() {
    const [period, setPeriod] = useState<Period>('daily');
    const [data, setData] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, [period]);

    const loadData = async () => {
        setLoading(true);
        try {
            let response;
            if (period === 'daily') {
                response = await emissionsAPI.getDaily(30);
            } else if (period === 'monthly') {
                response = await emissionsAPI.getMonthly(12);
            } else {
                response = await emissionsAPI.getYearly(5);
            }

            const emissions = response.data.emissions.reverse();
            setData(emissions);
        } catch (error) {
            console.error('Failed to load emissions:', error);
        }
        setLoading(false);
    };

    return (
        <div className="glass-card p-6">
            <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-semibold">Emission Trends</h3>

                <div className="flex gap-2">
                    {(['daily', 'monthly', 'yearly'] as Period[]).map((p) => (
                        <button
                            key={p}
                            onClick={() => setPeriod(p)}
                            className={`px-4 py-2 rounded-lg font-medium transition-all ${period === p
                                    ? 'bg-eco-green-500 text-white'
                                    : 'bg-dark-elevated text-gray-400 hover:bg-dark-elevated/80'
                                }`}
                        >
                            {p.charAt(0).toUpperCase() + p.slice(1)}
                        </button>
                    ))}
                </div>
            </div>

            {loading ? (
                <div className="h-80 flex items-center justify-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-4 border-eco-green-500 border-t-transparent" />
                </div>
            ) : data.length === 0 ? (
                <div className="h-80 flex items-center justify-center text-gray-500">
                    No emission data available
                </div>
            ) : (
                <ResponsiveContainer width="100%" height={320}>
                    <BarChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e2330" />
                        <XAxis dataKey="period" stroke="#6b7280" />
                        <YAxis stroke="#6b7280" label={{ value: 'CO₂ (kg)', angle: -90, position: 'insideLeft', fill: '#6b7280' }} />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: '#141824',
                                border: '1px solid rgba(255,255,255,0.1)',
                                borderRadius: '8px',
                            }}
                        />
                        <Legend />
                        <Bar dataKey="electricity_co2_kg" name="Electricity CO₂" fill="#10b981" />
                        <Bar dataKey="combustion_co2_kg" name="Combustion CO₂" fill="#fbbf24" />
                    </BarChart>
                </ResponsiveContainer>
            )}
        </div>
    );
}
