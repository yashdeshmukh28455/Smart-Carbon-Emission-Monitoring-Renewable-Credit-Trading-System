'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function Navigation() {
    const router = useRouter();

    return (
        <div className="flex justify-between items-center mb-6 pt-4 px-2">
            <button
                onClick={() => router.back()}
                className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-all backdrop-blur-sm border border-white/10"
            >
                <span>←</span>
                <span>Back</span>
            </button>

            <Link
                href="/dashboard"
                className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-all backdrop-blur-sm border border-white/10"
            >
                <span>🏠</span>
                <span>Home</span>
            </Link>
        </div>
    );
}
