'use client';

import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { predictionsAPI } from '@/lib/api';

interface PredictionGraphProps {
    annualLimit: number;
}

export default function PredictionGraph({ annualLimit }: PredictionGraphProps) {
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadPredictions();
    }, []);

    const loadPredictions = async () => {
        setLoading(true);
        try {
            const response = await predictionsAPI.getForecast(30);
            setData(response.data);
        } catch (error) {
            console.error('Failed to load predictions:', error);
        }
        setLoading(false);
    };

    if (loading) {
        return (
            <div className="glass-card p-6">
                <h3 className="text-xl font-semibold mb-4">AI Emission Predictions</h3>
                <div className="h-80 flex items-center justify-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-4 border-eco-green-500 border-t-transparent" />
                </div>
            </div>
        );
    }

    if (!data || !data.success) {
        return (
            <div className="glass-card p-6">
                <h3 className="text-xl font-semibold mb-4">AI Emission Predictions</h3>
                <div className="h-80 flex items-center justify-center text-gray-500">
                    {data?.message || 'Unable to generate predictions. Need more historical data.'}
                </div>
            </div>
        );
    }

    const chartData = data.predictions.map((p: any) => ({
        date: p.date,
        predicted: p.predicted_co2_kg,
    }));

    return (
        <div className="glass-card p-6">
            <div className="flex justify-between items-start mb-4">
                <div>
                    <h3 className="text-xl font-semibold mb-2">AI Emission Predictions</h3>
                    <p className="text-sm text-gray-400">Linear Regression Model • Next 30 Days</p>
                </div>

                {data.will_exceed_limit && (
                    <div className="bg-status-exceeded/20 border-2 border-status-exceeded text-status-exceeded px-4 py-2 rounded-lg animate-pulse-slow">
                        <span className="font-semibold">⚠ Warning: Limit Exceed Predicted</span>
                    </div>
                )}
            </div>

            <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-dark-elevated p-4 rounded-lg">
                    <div className="text-gray-400 text-sm">Current Emissions</div>
                    <div className="text-2xl font-bold text-eco-green-500">{data.current_emissions_kg.toFixed(2)} kg</div>
                </div>
                <div className="bg-dark-elevated p-4 rounded-lg">
                    <div className="text-gray-400 text-sm">Predicted (30d)</div>
                    <div className="text-2xl font-bold text-status-warning">{data.predicted_next_30d_kg.toFixed(2)} kg</div>
                </div>
                <div className="bg-dark-elevated p-4 rounded-lg">
                    <div className="text-gray-400 text-sm">Projected Total</div>
                    <div className={`text-2xl font-bold ${data.will_exceed_limit ? 'text-status-exceeded' : 'text-eco-green-500'}`}>
                        {data.projected_total_kg.toFixed(2)} kg
                    </div>
                </div>
            </div>

            <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e2330" />
                    <XAxis dataKey="date" stroke="#6b7280" />
                    <YAxis stroke="#6b7280" />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#141824',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '8px',
                        }}
                    />
                    <Line
                        type="monotone"
                        dataKey="predicted"
                        stroke="#10b981"
                        strokeWidth={2}
                        strokeDasharray="5 5"
                        dot={{ fill: '#10b981', r: 4 }}
                    />
                </LineChart>
            </ResponsiveContainer>

            <div className="mt-4 text-xs text-gray-500 text-center">
                Predictions generated using Linear Regression • Explainable AI
            </div>
        </div>
    );
}
