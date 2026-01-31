'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { emissionsAPI, demoAPI } from '@/lib/api';
import StatusBadge from '@/components/StatusBadge';
import EmissionGauge from '@/components/EmissionGauge';
import CarbonLimitMeter from '@/components/CarbonLimitMeter';
import EmissionChart from '@/components/EmissionChart';
import CreditPurchaseModal from '@/components/CreditPurchaseModal';
import PredictionGraph from '@/components/PredictionGraph';

export default function DashboardPage() {
    const router = useRouter();
    const { user, logout, isAuthenticated, loading: authLoading } = useAuth();
    const [status, setStatus] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [showCreditModal, setShowCreditModal] = useState(false);
    const [demoLoading, setDemoLoading] = useState(false);

    useEffect(() => {
        if (!authLoading && !isAuthenticated) {
            router.push('/login');
        }
    }, [isAuthenticated, authLoading, router]);

    useEffect(() => {
        if (isAuthenticated) {
            loadStatus();
        }
    }, [isAuthenticated]);

    const loadStatus = async () => {
        setLoading(true);
        try {
            const response = await emissionsAPI.getStatus();
            setStatus(response.data);
        } catch (error) {
            console.error('Failed to load status:', error);
        }
        setLoading(false);
    };

    const handleGenerateDemo = async () => {
        setDemoLoading(true);
        try {
            await demoAPI.simulateExceed();
            await loadStatus();
            alert('Demo data generated! Check your dashboard.');
        } catch (error) {
            console.error('Failed to generate demo:', error);
        }
        setDemoLoading(false);
    };

    if (authLoading || !user) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-16 w-16 border-4 border-eco-green-500 border-t-transparent" />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-dark-bg">
            {/* Header */}
            <header className="glass-card border-b border-white/10">
                <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
                    <div className="flex items-center gap-4">
                        <div className="text-3xl">🌍</div>
                        <div>
                            <h1 className="text-2xl font-bold text-gradient">Carbon Trading Platform</h1>
                            <p className="text-sm text-gray-400">{user.email}</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <button
                            onClick={handleGenerateDemo}
                            disabled={demoLoading}
                            className="px-4 py-2 bg-eco-green-500/20 text-eco-green-500 rounded-lg hover:bg-eco-green-500/30 transition-all"
                        >
                            {demoLoading ? '⏳ Generating...' : '🎲 Generate Demo Data'}
                        </button>
                        <button
                            onClick={logout}
                            className="px-4 py-2 bg-dark-elevated text-gray-400 rounded-lg hover:bg-dark-elevated/80 transition-all"
                        >
                            Logout
                        </button>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-6 py-8">
                {loading ? (
                    <div className="flex items-center justify-center py-20">
                        <div className="animate-spin rounded-full h-16 w-16 border-4 border-eco-green-500 border-t-transparent" />
                    </div>
                ) : status ? (
                    <div className="space-y-8">
                        {/* Status Overview */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div className="glass-card p-6">
                                <h3 className="text-gray-400 text-sm mb-2">Current Status</h3>
                                <StatusBadge status={status.status} percentage={status.percentage_used} />
                                <p className="text-sm text-gray-500 mt-4">{status.status_message}</p>
                            </div>

                            <div className="glass-card p-6">
                                <h3 className="text-gray-400 text-sm mb-2">Annual Carbon Limit</h3>
                                <div className="text-3xl font-bold text-eco-green-500">{status.annual_limit_kg.toFixed(2)}</div>
                                <p className="text-sm text-gray-500 mt-1">kg CO₂ per year</p>
                                <div className="mt-4 text-xs text-gray-600">
                                    {user.household.area_sqm} m² • {user.household.occupants} occupants
                                </div>
                            </div>

                            <div className="glass-card p-6">
                                <h3 className="text-gray-400 text-sm mb-2">Remaining Budget</h3>
                                <div className="text-3xl font-bold text-status-warning">{status.remaining_budget_kg.toFixed(2)}</div>
                                <p className="text-sm text-gray-500 mt-1">kg CO₂ remaining</p>
                            </div>
                        </div>

                        {/* Real-time Gauges */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <EmissionGauge
                                title="Electricity CO₂"
                                value={status.electricity_co2_kg}
                                unit="kg"
                                icon="⚡"
                                color="text-eco-green-500"
                            />
                            <EmissionGauge
                                title="Combustion CO₂"
                                value={status.combustion_co2_kg}
                                unit="kg"
                                icon="🔥"
                                color="text-status-warning"
                            />
                        </div>

                        {/* Carbon Limit Meter & Charts */}
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            <CarbonLimitMeter
                                percentage={status.percentage_used}
                                current={status.net_emissions_kg}
                                limit={status.annual_limit_kg}
                            />

                            <div className="lg:col-span-2">
                                <EmissionChart />
                            </div>
                        </div>

                        {/* Credit Purchase Section */}
                        {status.needs_credits && (
                            <div className="glass-card p-6 border-2 border-status-exceeded animate-glow">
                                <div className="flex justify-between items-center">
                                    <div>
                                        <h3 className="text-xl font-bold text-status-exceeded mb-2">⚠ Carbon Limit Exceeded</h3>
                                        <p className="text-gray-400">
                                            You've exceeded your limit by <span className="font-bold text-status-exceeded">{status.excess_co2_kg.toFixed(2)} kg CO₂</span>
                                        </p>
                                        <p className="text-sm text-gray-500 mt-2">
                                            Purchase renewable energy credits to neutralize your carbon footprint
                                        </p>
                                    </div>
                                    <button
                                        onClick={() => setShowCreditModal(true)}
                                        className="btn-gradient"
                                    >
                                        Purchase Credits
                                    </button>
                                </div>
                            </div>
                        )}

                        {/* AI Predictions */}
                        <PredictionGraph annualLimit={status.annual_limit_kg} />
                    </div>
                ) : (
                    <div className="text-center py-20">
                        <div className="text-6xl mb-4">📊</div>
                        <h2 className="text-2xl font-bold mb-4">No Data Yet</h2>
                        <p className="text-gray-400 mb-6">Generate demo data to see your dashboard in action</p>
                        <button onClick={handleGenerateDemo} className="btn-gradient">
                            Generate Demo Data
                        </button>
                    </div>
                )}
            </main>

            {/* Credit Purchase Modal */}
            {status && showCreditModal && (
                <CreditPurchaseModal
                    isOpen={showCreditModal}
                    onClose={() => setShowCreditModal(false)}
                    excessCO2={status.excess_co2_kg}
                    onPurchaseSuccess={loadStatus}
                />
            )}
        </div>
    );
}
