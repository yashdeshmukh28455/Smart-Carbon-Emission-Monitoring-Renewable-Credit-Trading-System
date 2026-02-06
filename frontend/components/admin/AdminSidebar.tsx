'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function AdminSidebar() {
    const pathname = usePathname();
    const router = useRouter();
    const [adminName, setAdminName] = useState('Admin');

    useEffect(() => {
        const storedAdmin = localStorage.getItem('adminUser');
        if (storedAdmin) {
            const { name } = JSON.parse(storedAdmin);
            setAdminName(name);
        }
    }, []);

    const logout = () => {
        localStorage.removeItem('adminToken');
        localStorage.removeItem('adminUser');
        router.push('/login');
    };

    const navItems = [
        { name: 'Dashboard', path: '/admin/dashboard' },
        { name: 'Live Trades', path: '/admin/trades' },
        { name: 'Manage Companies', path: '/admin/companies' },
    ];

    return (
        <div className="w-64 bg-slate-900 text-white min-h-screen flex flex-col">
            <div className="p-6 border-b border-slate-800">
                <h1 className="text-xl font-bold text-emerald-400">Carbon Admin</h1>
                <p className="text-sm text-slate-400 mt-1">Logged in as {adminName}</p>
            </div>

            <nav className="flex-1 p-4 space-y-2">
                {navItems.map((item) => {
                    const isActive = pathname === item.path;
                    return (
                        <Link
                            key={item.path}
                            href={item.path}
                            className={`block px-4 py-3 rounded-lg transition-colors ${isActive
                                ? 'bg-emerald-600 text-white'
                                : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                                }`}
                        >
                            {item.name}
                        </Link>
                    );
                })}
            </nav>

            <div className="p-4 border-t border-slate-800">
                <button
                    onClick={logout}
                    className="w-full px-4 py-2 bg-red-900/30 text-red-400 hover:bg-red-900/50 rounded-lg transition-colors"
                >
                    Logout
                </button>
            </div>
        </div>
    );
}
