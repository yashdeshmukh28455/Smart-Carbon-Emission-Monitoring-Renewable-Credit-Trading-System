'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import Navigation from '@/components/Navigation';

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
    const [showPassword, setShowPassword] = useState(false);

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
        <div className="min-h-screen flex flex-col items-center justify-center p-4 bg-gradient-radial from-dark-bg via-dark-bg to-eco-green-900/10">
            <div className="w-full max-w-4xl px-4 absolute top-4">
                <Navigation />
            </div>
            <div className="glass-card p-8 w-full max-w-md mt-12">
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
                        <div className="relative">
                            <input
                                type={showPassword ? "text" : "password"}
                                name="password"
                                value={formData.password}
                                onChange={handleChange}
                                className="input-field pr-10"
                                placeholder="••••••••"
                                required
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                            >
                                {showPassword ? (
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                                        <path strokeLinecap="round" strokeLinejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88" />
                                    </svg>
                                ) : (
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                                        <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                                        <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                                    </svg>
                                )}
                            </button>
                        </div>
                    </div>

                    <div>
                        <label className="block text-gray-400 mb-2 text-sm">Confirm Password</label>
                        <div className="relative">
                            <input
                                type={showPassword ? "text" : "password"}
                                name="confirmPassword"
                                value={formData.confirmPassword}
                                onChange={handleChange}
                                className="input-field pr-10"
                                placeholder="••••••••"
                                required
                            />
                        </div>
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
            </div >
        </div >
    );
}
