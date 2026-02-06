'use client';

import { useEffect, useState } from 'react';
import AdminLayout from '@/components/admin/AdminLayout';
import { adminClient } from '@/lib/adminApi';

interface Stats {
    total_users: number;
    total_companies: number;
    total_carbon_traded: number;
    total_volume_traded: number;
}

export default function AdminDashboard() {
    const [stats, setStats] = useState<Stats | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await adminClient.getStats();
                setStats(response.data.stats);
            } catch (error) {
                console.error('Failed to fetch stats:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    return (
        <AdminLayout>
            <h1 className="text-3xl font-bold text-gray-900 mb-8">Platform Overview</h1>

            {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 animate-pulse">
                    {[1, 2, 3, 4].map(i => (
                        <div key={i} className="h-32 bg-gray-200 rounded-xl"></div>
                    ))}
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <h3 className="text-sm font-medium text-gray-500 uppercase">Total Users</h3>
                        <p className="mt-2 text-3xl font-bold text-indigo-600">{stats?.total_users}</p>
                    </div>
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <h3 className="text-sm font-medium text-gray-500 uppercase">Active Companies</h3>
                        <p className="mt-2 text-3xl font-bold text-emerald-600">{stats?.total_companies}</p>
                    </div>
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <h3 className="text-sm font-medium text-gray-500 uppercase">Carbon Traded</h3>
                        <p className="mt-2 text-3xl font-bold text-blue-600">{stats?.total_carbon_traded.toFixed(1)} <span className="text-sm text-gray-400">kg</span></p>
                    </div>
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <h3 className="text-sm font-medium text-gray-500 uppercase">Trading Volume</h3>
                        <p className="mt-2 text-3xl font-bold text-purple-600">₹{stats?.total_volume_traded.toFixed(2)}</p>
                    </div>
                </div>
            )}

            <div className="mt-12 bg-white rounded-xl shadow-sm border border-gray-100 p-8 text-center">
                <h2 className="text-xl font-semibold text-gray-800">Welcome to the Admin Control Center</h2>
                <p className="mt-2 text-gray-500">Manage companies, monitor active trades, and oversee platform health from this dashboard.</p>
            </div>
        </AdminLayout>
    );
}
