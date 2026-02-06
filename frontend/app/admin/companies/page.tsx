'use client';

import { useEffect, useState } from 'react';
import AdminLayout from '@/components/admin/AdminLayout';
import { adminClient } from '@/lib/adminApi';

interface Company {
    _id: string;
    name: string;
    email: string;
    status: string;
    credits_sold_total: number;
    api_key: string;
}

export default function AdminCompanies() {
    const [companies, setCompanies] = useState<Company[]>([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);

    // Form state
    const [newName, setNewName] = useState('');
    const [newEmail, setNewEmail] = useState('');
    const [newDesc, setNewDesc] = useState('');
    const [newContact, setNewContact] = useState('');

    const fetchCompanies = async () => {
        try {
            const response = await adminClient.getCompanies();
            setCompanies(response.data.companies);
        } catch (error) {
            console.error('Failed to fetch companies:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCompanies();
    }, []);

    const handleAddCompany = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await adminClient.createCompany({
                name: newName,
                email: newEmail,
                description: newDesc,
                contact_person: newContact
            });
            setShowModal(false);
            setNewName('');
            setNewEmail('');
            setNewDesc('');
            setNewContact('');
            fetchCompanies();
        } catch (error) {
            console.error('Failed to add company:', error);
            alert('Failed to add company');
        }
    };

    const handleApprove = async (id: string) => {
        if (!confirm('Are you sure you want to approve this company?')) return;
        try {
            await adminClient.approveCompany(id);
            fetchCompanies();
        } catch (error) {
            console.error('Failed to approve company:', error);
        }
    };

    return (
        <AdminLayout>
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold text-gray-900">Manage Companies</h1>
                <button
                    onClick={() => setShowModal(true)}
                    className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors shadow-sm"
                >
                    + Add New Company
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {loading ? (
                    <p className="text-gray-500">Loading companies...</p>
                ) : companies.length === 0 ? (
                    <p className="text-gray-500">No companies registered yet.</p>
                ) : (
                    companies.map((company) => (
                        <div key={company._id} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col">
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h3 className="text-lg font-bold text-gray-900">{company.name}</h3>
                                    <p className="text-sm text-gray-500">{company.email}</p>
                                </div>
                                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${company.status === 'approved' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                                    }`}>
                                    {company.status}
                                </span>
                            </div>

                            <div className="flex-1 space-y-2 mb-4">
                                <div className="text-sm">
                                    <span className="text-gray-500">Credits Sold:</span>
                                    <span className="ml-2 font-medium">{company.credits_sold_total} kg</span>
                                </div>
                                <div className="text-xs font-mono bg-gray-50 p-2 rounded truncate" title={company.api_key}>
                                    Key: {company.api_key.substring(0, 10)}...
                                </div>
                            </div>

                            {company.status !== 'approved' && (
                                <button
                                    onClick={() => handleApprove(company._id)}
                                    className="w-full py-2 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 rounded-lg text-sm font-medium transition-colors"
                                >
                                    Approve Access
                                </button>
                            )}
                        </div>
                    ))
                )}
            </div>

            {/* Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
                        <h2 className="text-xl font-bold mb-4">Onboard New Company</h2>
                        <form onSubmit={handleAddCompany} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Company Name</label>
                                <input type="text" required value={newName} onChange={e => setNewName(e.target.value)} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Email</label>
                                <input type="email" required value={newEmail} onChange={e => setNewEmail(e.target.value)} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Contact Person</label>
                                <input type="text" required value={newContact} onChange={e => setNewContact(e.target.value)} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Description</label>
                                <textarea value={newDesc} onChange={e => setNewDesc(e.target.value)} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2" />
                            </div>
                            <div className="flex justify-end space-x-3 mt-6">
                                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Cancel</button>
                                <button type="submit" className="px-4 py-2 bg-emerald-600 text-white hover:bg-emerald-700 rounded-lg">Add Company</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </AdminLayout>
    );
}
