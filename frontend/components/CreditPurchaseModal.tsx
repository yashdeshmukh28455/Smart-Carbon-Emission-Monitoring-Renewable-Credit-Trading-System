'use client';

import React, { useState } from 'react';
import { creditsAPI } from '@/lib/api';

interface CreditPurchaseModalProps {
    isOpen: boolean;
    onClose: () => void;
    excessCO2: number;
    onPurchaseSuccess: () => void;
}

interface CreditType {
    type: string;
    name: string;
    description: string;
    icon: string;
    price_per_kg: number;
}

export default function CreditPurchaseModal({ isOpen, onClose, excessCO2, onPurchaseSuccess }: CreditPurchaseModalProps) {
    const [selectedType, setSelectedType] = useState<string>('solar');
    const [amount, setAmount] = useState<number>(excessCO2);
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);

    const creditTypes: CreditType[] = [
        { type: 'solar', name: 'Solar Energy Credits', description: 'Offset via solar power', icon: '☀️', price_per_kg: 0.15 },
        { type: 'wind', name: 'Wind Energy Credits', description: 'Offset via wind power', icon: '💨', price_per_kg: 0.12 },
        { type: 'bio', name: 'Bio-Energy Credits', description: 'Offset via biomass energy', icon: '🌱', price_per_kg: 0.10 },
    ];

    const selectedCredit = creditTypes.find(c => c.type === selectedType)!;
    const totalPrice = amount * selectedCredit.price_per_kg;

    const handlePurchase = async () => {
        setLoading(true);
        try {
            await creditsAPI.purchase(selectedType, amount);
            setSuccess(true);
            setTimeout(() => {
                onPurchaseSuccess();
                onClose();
                setSuccess(false);
            }, 2000);
        } catch (error) {
            console.error('Purchase failed:', error);
            alert('Failed to purchase credits');
        }
        setLoading(false);
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="glass-card p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                {success ? (
                    <div className="text-center py-12">
                        <div className="text-6xl mb-4">✓</div>
                        <h2 className="text-2xl font-bold text-eco-green-500 mb-2">Purchase Successful!</h2>
                        <p className="text-gray-400">Your carbon footprint has been neutralized</p>
                    </div>
                ) : (
                    <>
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-2xl font-bold">Purchase Renewable Credits</h2>
                            <button onClick={onClose} className="text-gray-400 hover:text-white text-2xl">×</button>
                        </div>

                        <div className="mb-6">
                            <p className="text-gray-400 mb-2">Excess CO₂ to offset:</p>
                            <p className="text-3xl font-bold text-status-exceeded">{excessCO2.toFixed(2)} kg</p>
                        </div>

                        <div className="mb-6">
                            <label className="block text-gray-400 mb-3">Select Credit Type:</label>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                {creditTypes.map((credit) => (
                                    <button
                                        key={credit.type}
                                        onClick={() => setSelectedType(credit.type)}
                                        className={`p-4 rounded-lg border-2 transition-all ${selectedType === credit.type
                                                ? 'border-eco-green-500 bg-eco-green-500/10'
                                                : 'border-white/10 hover:border-white/30'
                                            }`}
                                    >
                                        <div className="text-3xl mb-2">{credit.icon}</div>
                                        <div className="font-semibold mb-1">{credit.name}</div>
                                        <div className="text-sm text-gray-400">{credit.description}</div>
                                        <div className="text-eco-green-500 font-bold mt-2">${credit.price_per_kg}/kg</div>
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="mb-6">
                            <label className="block text-gray-400 mb-2">Amount (kg CO₂):</label>
                            <input
                                type="number"
                                value={amount}
                                onChange={(e) => setAmount(parseFloat(e.target.value) || 0)}
                                className="input-field"
                                min={0}
                                step={0.1}
                            />
                        </div>

                        <div className="bg-dark-elevated p-4 rounded-lg mb-6">
                            <div className="flex justify-between items-center">
                                <span className="text-gray-400">Total Price:</span>
                                <span className="text-2xl font-bold text-eco-green-500">${totalPrice.toFixed(2)} USD</span>
                            </div>
                            <div className="text-xs text-gray-500 mt-2">
                                Valid for 1 year from purchase date
                            </div>
                        </div>

                        <div className="flex gap-4">
                            <button
                                onClick={onClose}
                                className="flex-1 px-6 py-3 bg-dark-elevated text-gray-400 rounded-lg hover:bg-dark-elevated/80 transition-all"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handlePurchase}
                                disabled={loading || amount <= 0}
                                className="flex-1 btn-gradient disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {loading ? 'Processing...' : 'Purchase Credits'}
                            </button>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
