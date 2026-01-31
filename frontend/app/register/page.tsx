'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';

export default function RegisterPage() {
    const router = useRouter();
    const { register } = useAuth();
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        confirmPassword: '',
        area_sqm: '',
        occupants: '',
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        setLoading(true);

        try {
            await register(
                formData.email,
                formData.password,
                parseFloat(formData.area_sqm),
                parseInt(formData.occupants)
            );
            router.push('/dashboard');
        } catch (err: any) {
            setError(err.response?.data?.error || 'Registration failed');
        }
        setLoading(false);
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-radial from-dark-bg via-dark-bg to-eco-green-900/10">
            <div className="glass-card p-8 w-full max-w-md">
                <div className="text-center mb-8">
                    <div className="text-5xl mb-4">🌱</div>
                    <h1 className="text-3xl font-bold mb-2 text-gradient">Create Account</h1>
                    <p className="text-gray-400">Start monitoring your carbon footprint</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    {error && (
                        <div className="bg-status-exceeded/20 border border-status-exceeded text-status-exceeded px-4 py-3 rounded-lg text-sm">
                            {error}
                        </div>
                    )}

                    <div>
                        <label className="block text-gray-400 mb-2 text-sm">Email</label>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            className="input-field"
                            placeholder="your@email.com"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-gray-400 mb-2 text-sm">Password</label>
                        <input
                            type="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            className="input-field"
                            placeholder="••••••••"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-gray-400 mb-2 text-sm">Confirm Password</label>
                        <input
                            type="password"
                            name="confirmPassword"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            className="input-field"
                            placeholder="••••••••"
                            required
                        />
                    </div>

                    <div className="border-t border-white/10 pt-4 mt-4">
                        <h3 className="text-lg font-semibold mb-3 text-eco-green-500">Household Information</h3>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-gray-400 mb-2 text-sm">House Area (m²)</label>
                                <input
                                    type="number"
                                    name="area_sqm"
                                    value={formData.area_sqm}
                                    onChange={handleChange}
                                    className="input-field"
                                    placeholder="100"
                                    min="1"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-gray-400 mb-2 text-sm">Occupants</label>
                                <input
                                    type="number"
                                    name="occupants"
                                    value={formData.occupants}
                                    onChange={handleChange}
                                    className="input-field"
                                    placeholder="4"
                                    min="1"
                                    required
                                />
                            </div>
                        </div>

                        <p className="text-xs text-gray-500 mt-2">
                            Used to calculate your annual carbon limit
                        </p>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full btn-gradient disabled:opacity-50"
                    >
                        {loading ? 'Creating account...' : 'Create Account'}
                    </button>
                </form>

                <div className="mt-6 text-center">
                    <p className="text-gray-400 text-sm">
                        Already have an account?{' '}
                        <Link href="/login" className="text-eco-green-500 hover:text-eco-green-400 font-semibold">
                            Login
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}
