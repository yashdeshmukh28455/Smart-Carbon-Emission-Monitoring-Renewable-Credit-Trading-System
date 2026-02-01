'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { authAPI } from '@/lib/api';
import Navigation from '@/components/Navigation';

export default function ProfilePage() {
    const router = useRouter();
    const [profile, setProfile] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        loadProfile();
    }, []);

    const loadProfile = async () => {
        try {
            const response = await authAPI.getProfile();
            setProfile(response.data);
        } catch (err) {
            console.error('Failed to load profile:', err);
            setError('Failed to load profile data');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-white border-t-transparent"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
            <div className="max-w-4xl mx-auto">
                <Navigation />

                <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20 shadow-xl">
                    <div className="flex items-center gap-6 mb-8 border-b border-white/10 pb-6">
                        <div className="h-20 w-20 bg-gradient-to-tr from-green-400 to-blue-500 rounded-full flex items-center justify-center text-3xl font-bold text-white shadow-lg">
                            {profile?.email?.charAt(0).toUpperCase() || 'U'}
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold text-white">My Profile</h1>
                            <p className="text-gray-300">{profile?.email}</p>
                        </div>
                    </div>

                    {error && (
                        <div className="bg-red-500/20 border border-red-500/50 text-red-200 p-4 rounded-xl mb-6">
                            {error}
                        </div>
                    )}

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        {/* Household Info */}
                        <div className="bg-white/5 rounded-xl p-6 border border-white/10">
                            <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                                🏠 Household Details
                            </h2>
                            <div className="space-y-4">
                                <div className="flex justify-between items-center py-2 border-b border-white/5">
                                    <span className="text-gray-400">Area Size</span>
                                    <span className="text-white font-mono text-lg">{profile?.household?.area_sqm} m²</span>
                                </div>
                                <div className="flex justify-between items-center py-2 border-b border-white/5">
                                    <span className="text-gray-400">Occupants</span>
                                    <span className="text-white font-mono text-lg">{profile?.household?.occupants} People</span>
                                </div>
                                <div className="flex justify-between items-center py-2">
                                    <span className="text-gray-400">Joined</span>
                                    <span className="text-white">{new Date(profile?.created_at).toLocaleDateString()}</span>
                                </div>
                            </div>
                        </div>

                        {/* Carbon Limit Info */}
                        <div className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 rounded-xl p-6 border border-green-500/20">
                            <h2 className="text-xl font-semibold text-green-400 mb-4 flex items-center gap-2">
                                🌿 Carbon Limit
                            </h2>
                            <div className="text-center py-4">
                                <p className="text-sm text-gray-400 mb-2">Annual Allowance</p>
                                <p className="text-4xl font-bold text-white mb-2">
                                    {profile?.household?.annual_carbon_limit_kg?.toLocaleString()} kg
                                </p>
                                <p className="text-sm text-green-300">of CO2 emissions</p>
                            </div>
                            <div className="mt-4 text-xs text-gray-400 text-center px-4">
                                Based on your household size and occupants. You can increase this limit by purchasing renewable energy credits.
                            </div>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="mt-8 flex gap-4">
                        <button
                            onClick={() => router.push('/trades')}
                            className="flex-1 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white py-3 rounded-xl font-semibold transition-all shadow-lg hover:shadow-blue-500/25"
                        >
                            Buy Credits
                        </button>
                        <button
                            onClick={() => router.push('/dashboard')}
                            className="flex-1 bg-white/10 hover:bg-white/20 text-white py-3 rounded-xl font-semibold transition-all border border-white/10"
                        >
                            View Dashboard
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
