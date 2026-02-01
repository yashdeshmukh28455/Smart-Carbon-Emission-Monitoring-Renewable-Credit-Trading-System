'use client';

import { useState, useEffect } from 'react';
import { marketplaceAPI, creditsAPI } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import Navigation from '@/components/Navigation';

export default function TradesPage() {
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState('listings');
    const [myListings, setMyListings] = useState([]);
    const [myPurchases, setMyPurchases] = useState([]);
    const [loading, setLoading] = useState(true);

    // Credit Purchase State
    const [creditTypes, setCreditTypes] = useState([]);
    const [selectedCredit, setSelectedCredit] = useState<any>(null);
    const [purchaseAmount, setPurchaseAmount] = useState('');
    const [purchaseLoading, setPurchaseLoading] = useState(false);

    useEffect(() => {
        loadTrades();
        loadCreditTypes();
    }, []);

    const loadTrades = async () => {
        try {
            setLoading(true);
            const response = await marketplaceAPI.getMyTrades();
            setMyListings(response.data.trades.sell_listings || []);
            setMyPurchases(response.data.trades.purchases || []);
        } catch (error) {
            console.error('Error loading trades:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadCreditTypes = async () => {
        try {
            const response = await creditsAPI.getTypes();
            setCreditTypes(response.data.credit_types || []);
        } catch (error) {
            console.error('Error loading credit types:', error);
        }
    };

    const handleCancelListing = async (listingId: string) => {
        if (!confirm('Are you sure you want to cancel this listing?')) return;

        try {
            await marketplaceAPI.cancelListing(listingId);
            alert('Listing cancelled successfully');
            loadTrades();
        } catch (error: any) {
            alert(error.response?.data?.error || 'Failed to cancel listing');
        }
    };

    const handlePurchaseCredit = async () => {
        if (!selectedCredit || !purchaseAmount) return;

        try {
            setPurchaseLoading(true);
            await creditsAPI.purchase(selectedCredit.type, parseFloat(purchaseAmount));
            alert(`Successfully purchased ${purchaseAmount} kg of ${selectedCredit.name}`);
            setPurchaseAmount('');
            setSelectedCredit(null);
            loadTrades(); // Refresh purchases
            setActiveTab('purchases');
        } catch (error: any) {
            alert(error.response?.data?.error || 'Failed to purchase credits');
        } finally {
            setPurchaseLoading(false);
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

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'active': return 'bg-green-500/20 text-green-400 border-green-500/30';
            case 'sold': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
            case 'cancelled': return 'bg-red-500/20 text-red-400 border-red-500/30';
            case 'completed': return 'bg-green-500/20 text-green-400 border-green-500/30';
            case 'pending': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
            default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
            <div className="max-w-7xl mx-auto">
                <Navigation />

                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold text-white mb-2">
                        📊 My Trading Dashboard
                    </h1>
                    <p className="text-gray-300">Manage your carbon credit listings and purchases</p>
                </div>

                {/* Tabs */}
                <div className="flex flex-wrap gap-4 mb-8">
                    <button
                        onClick={() => setActiveTab('listings')}
                        className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 ${activeTab === 'listings'
                            ? 'bg-white text-purple-900 shadow-lg'
                            : 'bg-white/10 text-white hover:bg-white/20'
                            }`}
                    >
                        My Listings ({myListings.length})
                    </button>
                    <button
                        onClick={() => setActiveTab('purchases')}
                        className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 ${activeTab === 'purchases'
                            ? 'bg-white text-purple-900 shadow-lg'
                            : 'bg-white/10 text-white hover:bg-white/20'
                            }`}
                    >
                        My Purchases ({myPurchases.length})
                    </button>
                    <button
                        onClick={() => setActiveTab('buy_credits')}
                        className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 ${activeTab === 'buy_credits'
                            ? 'bg-gradient-to-r from-green-400 to-emerald-600 text-white shadow-lg'
                            : 'bg-white/10 text-emerald-300 hover:bg-white/20 border border-emerald-500/30'
                            }`}
                    >
                        🌿 Buy Credits
                    </button>
                </div>

                {loading ? (
                    <div className="text-center py-20">
                        <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-white border-t-transparent"></div>
                        <p className="text-white mt-4">Loading your trades...</p>
                    </div>
                ) : (
                    <>
                        {/* My Listings Tab */}
                        {activeTab === 'listings' && (
                            <div>
                                {myListings.length === 0 ? (
                                    <div className="text-center py-20 bg-white/5 rounded-2xl backdrop-blur-sm">
                                        <p className="text-gray-300 text-xl">No listings yet</p>
                                        <p className="text-gray-400 mt-2">Create a listing to start selling credits</p>
                                        <a
                                            href="/marketplace"
                                            className="inline-block mt-4 px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all"
                                        >
                                            Go to Marketplace
                                        </a>
                                    </div>
                                ) : (
                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                        {myListings.map((listing: any) => (
                                            <div
                                                key={listing.listing_id}
                                                className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20 hover:border-white/40 transition-all duration-300"
                                            >
                                                {/* Status Badge */}
                                                <div className={`inline-block px-4 py-1 rounded-full text-sm font-semibold mb-4 border ${getStatusColor(listing.status)}`}>
                                                    {listing.status.toUpperCase()}
                                                </div>

                                                {/* Credit Type */}
                                                <div className="flex items-center gap-2 mb-4">
                                                    <span className="text-3xl">{getCreditIcon(listing.credit_type)}</span>
                                                    <span className="text-xl font-bold text-white">{listing.credit_type.toUpperCase()}</span>
                                                </div>

                                                {/* Details */}
                                                <div className="space-y-2 mb-4">
                                                    <div className="flex justify-between">
                                                        <span className="text-gray-400">Amount:</span>
                                                        <span className="text-white font-semibold">{listing.amount_kg_co2} kg</span>
                                                    </div>
                                                    <div className="flex justify-between">
                                                        <span className="text-gray-400">Price/kg:</span>
                                                        <span className="text-green-400 font-semibold">₹{listing.price_per_kg}</span>
                                                    </div>
                                                    <div className="flex justify-between">
                                                        <span className="text-gray-400">Total:</span>
                                                        <span className="text-white font-bold">₹{listing.total_price.toFixed(2)}</span>
                                                    </div>
                                                    {listing.sold_amount > 0 && (
                                                        <div className="flex justify-between">
                                                            <span className="text-gray-400">Sold:</span>
                                                            <span className="text-blue-400 font-semibold">{listing.sold_amount} kg</span>
                                                        </div>
                                                    )}
                                                </div>

                                                {/* Stats */}
                                                <div className="text-sm text-gray-400 mb-4">
                                                    <p>👁️ {listing.views} views</p>
                                                    <p>📅 {new Date(listing.created_at).toLocaleDateString()}</p>
                                                </div>

                                                {/* Actions */}
                                                {listing.status === 'active' && (
                                                    <button
                                                        onClick={() => handleCancelListing(listing.listing_id)}
                                                        className="w-full px-4 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-all border border-red-500/30"
                                                    >
                                                        Cancel Listing
                                                    </button>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}

                        {/* My Purchases Tab */}
                        {activeTab === 'purchases' && (
                            <div>
                                {myPurchases.length === 0 ? (
                                    <div className="text-center py-20 bg-white/5 rounded-2xl backdrop-blur-sm">
                                        <p className="text-gray-300 text-xl">No purchases yet</p>
                                        <p className="text-gray-400 mt-2">Browse the marketplace to buy credits</p>
                                        <a
                                            href="/marketplace"
                                            className="inline-block mt-4 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all"
                                        >
                                            Browse Marketplace
                                        </a>
                                    </div>
                                ) : (
                                    <div className="space-y-4">
                                        {myPurchases.map((purchase: any) => (
                                            <div
                                                key={purchase.payment_id}
                                                className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20"
                                            >
                                                <div className="flex justify-between items-start mb-4">
                                                    <div>
                                                        <p className="text-sm text-gray-400">Transaction ID</p>
                                                        <p className="text-white font-mono">{purchase.transaction_id}</p>
                                                    </div>
                                                    <div className={`px-4 py-1 rounded-full text-sm font-semibold border ${getStatusColor(purchase.status)}`}>
                                                        {purchase.status.toUpperCase()}
                                                    </div>
                                                </div>

                                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                                    <div>
                                                        <p className="text-sm text-gray-400">Amount</p>
                                                        <p className="text-white font-semibold">{purchase.amount_kg_co2} kg</p>
                                                    </div>
                                                    <div>
                                                        <p className="text-sm text-gray-400">Total Paid</p>
                                                        <p className="text-green-400 font-semibold">{purchase.credit_type ? `$${purchase.price_usd || '?'}` : `₹${purchase.total_amount.toFixed(2)}`}</p>
                                                    </div>
                                                    <div>
                                                        <p className="text-sm text-gray-400">Type</p>
                                                        <p className="text-white font-semibold">{purchase.credit_type ? purchase.credit_type.toUpperCase() : purchase.payment_method.toUpperCase()}</p>
                                                    </div>
                                                    <div>
                                                        <p className="text-sm text-gray-400">Date</p>
                                                        <p className="text-white">{new Date(purchase.created_at).toLocaleDateString()}</p>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Buy Credits Tab */}
                        {activeTab === 'buy_credits' && (
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                                {/* Credit Options */}
                                <div className="space-y-4">
                                    <h2 className="text-2xl font-bold text-white mb-6">Select Carbon Credit Type</h2>
                                    {creditTypes.map((credit: any) => (
                                        <div
                                            key={credit.type}
                                            onClick={() => setSelectedCredit(credit)}
                                            className={`cursor-pointer p-6 rounded-2xl border transition-all duration-300 ${selectedCredit?.type === credit.type
                                                ? 'bg-gradient-to-r from-green-500/20 to-emerald-600/20 border-green-500 scale-105 shadow-xl shadow-green-500/10'
                                                : 'bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/30'
                                                }`}
                                        >
                                            <div className="flex items-center gap-4">
                                                <div className="text-4xl">{credit.icon}</div>
                                                <div className="flex-1">
                                                    <h3 className="text-xl font-bol text-white">{credit.name}</h3>
                                                    <p className="text-sm text-gray-400">{credit.description}</p>
                                                </div>
                                                <div className="text-right">
                                                    <p className="text-2xl font-bold text-green-400">₹{credit.price_per_kg}</p>
                                                    <p className="text-xs text-gray-500">per kg CO2</p>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                {/* Purchase Form */}
                                <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20 h-fit sticky top-6">
                                    <h2 className="text-2xl font-bold text-white mb-6">Purchase Summary</h2>

                                    {!selectedCredit ? (
                                        <div className="text-center py-10 text-gray-400">
                                            <p className="text-4xl mb-4">👈</p>
                                            <p>Select a credit type to proceed</p>
                                        </div>
                                    ) : (
                                        <div className="space-y-6">
                                            <div className="flex items-center gap-4 p-4 bg-white/5 rounded-xl border border-white/10">
                                                <span className="text-3xl">{selectedCredit.icon}</span>
                                                <div>
                                                    <p className="text-sm text-gray-400">Selected Type</p>
                                                    <p className="text-lg font-bold text-white">{selectedCredit.name}</p>
                                                </div>
                                            </div>

                                            <div>
                                                <label className="block text-sm text-gray-400 mb-2">Amount (kg CO2)</label>
                                                <input
                                                    type="number"
                                                    value={purchaseAmount}
                                                    onChange={(e) => setPurchaseAmount(e.target.value)}
                                                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-green-500 transition-colors"
                                                    placeholder="Enter amount to offset..."
                                                    min="1"
                                                />
                                            </div>

                                            <div className="border-t border-white/10 pt-4">
                                                <div className="flex justify-between items-center mb-2">
                                                    <span className="text-gray-400">Price per kg</span>
                                                    <span className="text-white">₹{selectedCredit.price_per_kg}</span>
                                                </div>
                                                <div className="flex justify-between items-center text-xl font-bold">
                                                    <span className="text-white">Total Cost</span>
                                                    <span className="text-green-400">
                                                        ₹{((parseFloat(purchaseAmount) || 0) * selectedCredit.price_per_kg).toFixed(2)}
                                                    </span>
                                                </div>
                                                <p className="text-xs text-right text-gray-500 mt-1">
                                                    + Applies immediately to your carbon limit
                                                </p>
                                            </div>

                                            <button
                                                onClick={handlePurchaseCredit}
                                                disabled={purchaseLoading || !purchaseAmount || parseFloat(purchaseAmount) <= 0}
                                                className={`w-full py-4 rounded-xl font-bold text-lg transition-all shadow-lg ${purchaseLoading || !purchaseAmount || parseFloat(purchaseAmount) <= 0
                                                    ? 'bg-gray-600 cursor-not-allowed opacity-50'
                                                    : 'bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white hover:shadow-green-500/25'
                                                    }`}
                                            >
                                                {purchaseLoading ? 'Processing...' : 'Confirm Purchase'}
                                            </button>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}
