'use client';

import { useState, useEffect } from 'react';
import { marketplaceAPI } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import Navigation from '@/components/Navigation';

interface Listing {
    listing_id: string;
    seller_id: string;
    credit_type: string;
    amount_kg_co2: number;
    price_per_kg: number;
    total_price: number;
    status: string;
    created_at: string;
    views: number;
}

export default function MarketplacePage() {
    const { isAuthenticated } = useAuth();
    const [listings, setListings] = useState<Listing[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const [sortBy, setSortBy] = useState('price');
    const [selectedListing, setSelectedListing] = useState<Listing | null>(null);
    const [showBuyModal, setShowBuyModal] = useState(false);
    const [showSellModal, setShowSellModal] = useState(false);

    useEffect(() => {
        loadListings();
    }, [filter]);

    const loadListings = async () => {
        try {
            setLoading(true);
            const filters = filter !== 'all' ? { credit_type: filter } : {};
            const response = await marketplaceAPI.getListings(filters);
            let data = response.data.listings || [];

            // Sort listings
            if (sortBy === 'price') {
                data.sort((a: Listing, b: Listing) => a.price_per_kg - b.price_per_kg);
            } else if (sortBy === 'amount') {
                data.sort((a: Listing, b: Listing) => b.amount_kg_co2 - a.amount_kg_co2);
            }

            setListings(data);
        } catch (error) {
            console.error('Error loading listings:', error);
        } finally {
            setLoading(false);
        }
    };

    const getCreditIcon = (type: string) => {
        switch (type) {
            case 'solar': return '☀️';
            case 'wind': return '💨';
            case 'bio': return '🌱';
            default: return '⚡';
        }
    };

    const getCreditColor = (type: string) => {
        switch (type) {
            case 'solar': return 'from-yellow-400 to-orange-500';
            case 'wind': return 'from-blue-400 to-cyan-500';
            case 'bio': return 'from-green-400 to-emerald-500';
            default: return 'from-purple-400 to-pink-500';
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
            <div className="max-w-7xl mx-auto">
                <Navigation />
            </div>
            {/* Header */}
            <div className="max-w-7xl mx-auto mb-8">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h1 className="text-4xl font-bold text-white mb-2">
                            🏪 Carbon Credit Marketplace
                        </h1>
                        <p className="text-gray-300">Trade renewable energy credits with other users</p>
                    </div>
                    {isAuthenticated && (
                        <button
                            onClick={() => setShowSellModal(true)}
                            className="px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl font-semibold hover:shadow-lg hover:shadow-green-500/50 transition-all duration-300 transform hover:scale-105"
                        >
                            + Sell Credits
                        </button>
                    )}
                </div>

                {/* Filters */}
                <div className="flex gap-4 mb-6 flex-wrap">
                    <div className="flex gap-2">
                        {['all', 'solar', 'wind', 'bio'].map((type) => (
                            <button
                                key={type}
                                onClick={() => setFilter(type)}
                                className={`px-4 py-2 rounded-lg font-medium transition-all duration-300 ${filter === type
                                    ? 'bg-white text-purple-900 shadow-lg'
                                    : 'bg-white/10 text-white hover:bg-white/20'
                                    }`}
                            >
                                {type.charAt(0).toUpperCase() + type.slice(1)}
                            </button>
                        ))}
                    </div>

                    <select
                        value={sortBy}
                        onChange={(e) => {
                            setSortBy(e.target.value);
                            loadListings();
                        }}
                        className="px-4 py-2 rounded-lg bg-white/10 text-white border border-white/20 focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                        <option value="price">Sort by Price</option>
                        <option value="amount">Sort by Amount</option>
                    </select>
                </div>
            </div>

            {/* Listings Grid */}
            <div className="max-w-7xl mx-auto">
                {loading ? (
                    <div className="text-center py-20">
                        <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-white border-t-transparent"></div>
                        <p className="text-white mt-4">Loading marketplace...</p>
                    </div>
                ) : listings.length === 0 ? (
                    <div className="text-center py-20 bg-white/5 rounded-2xl backdrop-blur-sm">
                        <p className="text-gray-300 text-xl">No listings available</p>
                        <p className="text-gray-400 mt-2">Be the first to sell credits!</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {listings.map((listing) => (
                            <div
                                key={listing.listing_id}
                                className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20 hover:border-white/40 transition-all duration-300 hover:transform hover:scale-105 hover:shadow-2xl cursor-pointer"
                                onClick={() => {
                                    setSelectedListing(listing);
                                    setShowBuyModal(true);
                                }}
                            >
                                {/* Credit Type Badge */}
                                <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r ${getCreditColor(listing.credit_type)} text-white font-semibold mb-4`}>
                                    <span className="text-2xl">{getCreditIcon(listing.credit_type)}</span>
                                    <span>{listing.credit_type.toUpperCase()}</span>
                                </div>

                                {/* Amount */}
                                <div className="mb-4">
                                    <p className="text-gray-400 text-sm">Available Amount</p>
                                    <p className="text-3xl font-bold text-white">{listing.amount_kg_co2.toFixed(2)} <span className="text-lg text-gray-300">kg CO₂</span></p>
                                </div>

                                {/* Price */}
                                <div className="mb-4">
                                    <p className="text-gray-400 text-sm">Price per kg</p>
                                    <p className="text-2xl font-bold text-green-400">₹{listing.price_per_kg.toFixed(2)}</p>
                                </div>

                                {/* Total Price */}
                                <div className="mb-4 pb-4 border-b border-white/10">
                                    <p className="text-gray-400 text-sm">Total Price</p>
                                    <p className="text-xl font-bold text-white">₹{listing.total_price.toFixed(2)}</p>
                                </div>

                                {/* Stats */}
                                <div className="flex justify-between text-sm text-gray-400">
                                    <span>👁️ {listing.views} views</span>
                                    <span>🕐 {new Date(listing.created_at).toLocaleDateString()}</span>
                                </div>

                                {/* Buy Button */}
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setSelectedListing(listing);
                                        setShowBuyModal(true);
                                    }}
                                    className="w-full mt-4 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-semibold hover:shadow-lg hover:shadow-purple-500/50 transition-all duration-300"
                                >
                                    Buy Now
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Buy Modal */}
            {showBuyModal && selectedListing && (
                <BuyModal
                    listing={selectedListing}
                    onClose={() => {
                        setShowBuyModal(false);
                        setSelectedListing(null);
                    }}
                    onSuccess={() => {
                        loadListings();
                        setShowBuyModal(false);
                        setSelectedListing(null);
                    }}
                />
            )}

            {/* Sell Modal */}
            {showSellModal && (
                <SellModal
                    onClose={() => setShowSellModal(false)}
                    onSuccess={() => {
                        loadListings();
                        setShowSellModal(false);
                    }}
                />
            )}
        </div>
    );
}

// Buy Modal Component
function BuyModal({ listing, onClose, onSuccess }: any) {
    const [amount, setAmount] = useState(listing.amount_kg_co2);
    const [paymentMethod, setPaymentMethod] = useState('upi');
    const [step, setStep] = useState(1); // 1: Amount, 2: Payment, 3: QR Code, 4: Success
    const [payment, setPayment] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    const totalPrice = amount * listing.price_per_kg;

    const handleInitiatePayment = async () => {
        try {
            setLoading(true);
            const response = await marketplaceAPI.initiatePurchase(listing.listing_id, {
                amount_kg_co2: amount,
                payment_method: paymentMethod
            });
            setPayment(response.data.payment);
            setStep(3);
        } catch (error: any) {
            alert(error.response?.data?.error || 'Failed to initiate payment');
        } finally {
            setLoading(false);
        }
    };

    const handleCompletePayment = async () => {
        try {
            setLoading(true);
            await marketplaceAPI.completePayment(payment.payment_id, {
                payment_reference: `UPI${Date.now()}`
            });
            setStep(4); // Show success step
        } catch (error: any) {
            alert(error.response?.data?.error || 'Payment failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-8 max-w-md w-full border border-white/20 shadow-2xl">
                <h2 className="text-2xl font-bold text-white mb-6">Buy Carbon Credits</h2>

                {step === 1 && (
                    <div>
                        <div className="mb-4">
                            <label className="text-gray-300 block mb-2">Amount (kg CO₂)</label>
                            <input
                                type="number"
                                value={amount}
                                onChange={(e) => setAmount(parseFloat(e.target.value))}
                                max={listing.amount_kg_co2}
                                className="w-full px-4 py-3 rounded-lg bg-white/10 text-white border border-white/20 focus:outline-none focus:ring-2 focus:ring-purple-500"
                            />
                            <p className="text-sm text-gray-400 mt-1">Max: {listing.amount_kg_co2} kg</p>
                        </div>

                        <div className="mb-6 p-4 bg-white/5 rounded-lg">
                            <div className="flex justify-between mb-2">
                                <span className="text-gray-300">Price per kg:</span>
                                <span className="text-white font-semibold">₹{listing.price_per_kg}</span>
                            </div>
                            <div className="flex justify-between text-xl font-bold">
                                <span className="text-gray-300">Total:</span>
                                <span className="text-green-400">₹{totalPrice.toFixed(2)}</span>
                            </div>
                        </div>

                        <div className="flex gap-3">
                            <button
                                onClick={onClose}
                                className="flex-1 px-6 py-3 bg-white/10 text-white rounded-xl hover:bg-white/20 transition-all"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={() => setStep(2)}
                                className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all"
                            >
                                Continue
                            </button>
                        </div>
                    </div>
                )}

                {step === 2 && (
                    <div>
                        <p className="text-gray-300 mb-4 font-medium">Select Payment Method</p>

                        <div className="grid grid-cols-2 gap-3 mb-6">
                            {[
                                { id: 'upi', label: 'UPI', icon: '📱' },
                                { id: 'qr', label: 'QR Scan', icon: '📷' },
                                { id: 'card', label: 'Card', icon: '💳' },
                                { id: 'wallet', label: 'Wallet', icon: '👛' },
                                { id: 'netbanking', label: 'Net Banking', icon: '🏦' }
                            ].map((method) => (
                                <button
                                    key={method.id}
                                    onClick={() => setPaymentMethod(method.id)}
                                    className={`p-4 rounded-xl border transition-all duration-200 flex flex-col items-center gap-2 ${paymentMethod === method.id
                                        ? 'border-green-500 bg-green-500/20 text-white'
                                        : 'border-white/10 bg-white/5 text-gray-400 hover:bg-white/10 hover:border-white/20'
                                        }`}
                                >
                                    <span className="text-2xl mb-1">{method.icon}</span>
                                    <span className="font-semibold text-sm">{method.label}</span>
                                </button>
                            ))}
                        </div>

                        <div className="flex gap-3">
                            <button
                                onClick={() => setStep(1)}
                                className="flex-1 px-6 py-3 bg-white/10 text-white rounded-xl hover:bg-white/20 transition-all"
                            >
                                Back
                            </button>
                            <button
                                onClick={handleInitiatePayment}
                                disabled={loading}
                                className="flex-1 px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all disabled:opacity-50"
                            >
                                {loading ? 'Processing...' : 'Pay Now'}
                            </button>
                        </div>
                    </div>
                )}

                {step === 3 && payment && (
                    <div className="text-center">
                        <p className="text-gray-300 mb-4">Scan QR Code to Pay</p>

                        {payment.qr_code && (
                            <div className="mb-4 p-4 bg-white rounded-lg">
                                <img src={payment.qr_code} alt="Payment QR" className="w-64 h-64 mx-auto" />
                            </div>
                        )}

                        {payment.upi_id && (
                            <div className="mb-4 p-4 bg-white/10 rounded-lg">
                                <p className="text-sm text-gray-400">UPI ID:</p>
                                <p className="text-white font-mono">{payment.upi_id}</p>
                            </div>
                        )}

                        <div className="mb-4 p-4 bg-white/10 rounded-lg">
                            <p className="text-sm text-gray-400">Amount to Pay:</p>
                            <p className="text-2xl font-bold text-green-400">₹{payment.total_amount.toFixed(2)}</p>
                        </div>

                        <button
                            onClick={handleCompletePayment}
                            disabled={loading}
                            className="w-full px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all disabled:opacity-50"
                        >
                            {loading ? 'Verifying...' : 'I have paid'}
                        </button>

                        <button
                            onClick={onClose}
                            className="w-full mt-3 px-6 py-3 bg-white/10 text-white rounded-xl hover:bg-white/20 transition-all"
                        >
                            Cancel
                        </button>
                    </div>
                )}

                {step === 4 && (
                    <div className="text-center py-8">
                        <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
                            <span className="text-3xl">✓</span>
                        </div>
                        <h3 className="text-2xl font-bold text-white mb-2">Purchase Successful!</h3>
                        <p className="text-gray-300 mb-6">
                            Credits have been added to your account and your carbon limit has been increased.
                        </p>
                        <button
                            onClick={onSuccess}
                            className="px-8 py-3 bg-white text-slate-900 rounded-xl font-bold hover:bg-gray-100 transition-all"
                        >
                            Done
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}

// Sell Modal Component
function SellModal({ onClose, onSuccess }: any) {
    const [creditType, setCreditType] = useState('solar');
    const [amount, setAmount] = useState('');
    const [price, setPrice] = useState('5'); // Default to minimum price
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            setLoading(true);
            await marketplaceAPI.createListing({
                credit_type: creditType,
                amount_kg_co2: parseFloat(amount),
                price_per_kg: parseFloat(price)
            });
            alert('Listing created successfully!');
            onSuccess();
        } catch (error: any) {
            alert(error.response?.data?.error || 'Failed to create listing');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-8 max-w-md w-full border border-white/20 shadow-2xl">
                <h2 className="text-2xl font-bold text-white mb-6">Sell Carbon Credits</h2>

                <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                        <label className="text-gray-300 block mb-2">Credit Type</label>
                        <select
                            value={creditType}
                            onChange={(e) => setCreditType(e.target.value)}
                            className="w-full px-4 py-3 rounded-lg bg-white/10 text-white border border-white/20 focus:outline-none focus:ring-2 focus:ring-purple-500"
                        >
                            <option value="solar">Solar</option>
                            <option value="wind">Wind</option>
                            <option value="bio">Bio</option>
                        </select>
                    </div>

                    <div className="mb-4">
                        <label className="text-gray-300 block mb-2">Amount (kg CO₂)</label>
                        <input
                            type="number"
                            value={amount}
                            onChange={(e) => setAmount(e.target.value)}
                            required
                            step="0.01"
                            className="w-full px-4 py-3 rounded-lg bg-white/10 text-white border border-white/20 focus:outline-none focus:ring-2 focus:ring-purple-500"
                        />
                    </div>

                    <div className="mb-6">
                        <label className="text-gray-300 block mb-2">Price per kg (₹)</label>
                        <input
                            type="number"
                            value={price}
                            onChange={(e) => setPrice(e.target.value)}
                            required
                            min="5"
                            step="0.01"
                            className="w-full px-4 py-3 rounded-lg bg-white/10 text-white border border-white/20 focus:outline-none focus:ring-2 focus:ring-purple-500"
                        />
                        <p className="text-sm text-gray-400 mt-1">Minimum price: ₹5.00 per kg</p>
                    </div>

                    {amount && price && (
                        <div className="mb-6 p-4 bg-green-500/20 rounded-lg border border-green-500/30">
                            <p className="text-sm text-gray-300">Total Listing Value:</p>
                            <p className="text-2xl font-bold text-green-400">₹{(parseFloat(amount) * parseFloat(price)).toFixed(2)}</p>
                        </div>
                    )}

                    <div className="flex gap-3">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 px-6 py-3 bg-white/10 text-white rounded-xl hover:bg-white/20 transition-all"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="flex-1 px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all disabled:opacity-50"
                        >
                            {loading ? 'Creating...' : 'Create Listing'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
