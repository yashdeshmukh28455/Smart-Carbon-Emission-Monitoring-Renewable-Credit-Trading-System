'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '@/lib/api';
import { jwtDecode } from 'jwt-decode';

interface User {
    user_id: string;
    email: string;
    household: {
        area_sqm: number;
        occupants: number;
        annual_carbon_limit_kg: number;
    };
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    login: (email: string, password: string) => Promise<void>;
    register: (email: string, password: string, area_sqm: number, occupants: number) => Promise<void>;
    logout: () => void;
    isAuthenticated: boolean;
    loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check for existing token
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
            try {
                const decoded: any = jwtDecode(storedToken);
                // Check if token is expired
                if (decoded.exp * 1000 > Date.now()) {
                    setToken(storedToken);
                    loadUserProfile(storedToken);
                } else {
                    localStorage.removeItem('token');
                }
            } catch (error) {
                localStorage.removeItem('token');
            }
        }
        setLoading(false);
    }, []);

    const loadUserProfile = async (authToken: string) => {
        try {
            const response = await authAPI.getProfile();
            setUser(response.data);
        } catch (error) {
            console.error('Failed to load user profile:', error);
            logout();
        }
    };

    const login = async (email: string, password: string) => {
        const response = await authAPI.login(email, password);
        const { access_token, ...userData } = response.data;

        localStorage.setItem('token', access_token);
        setToken(access_token);
        setUser(userData);
    };

    const register = async (email: string, password: string, area_sqm: number, occupants: number) => {
        const response = await authAPI.register(email, password, area_sqm, occupants);
        const { access_token, ...userData } = response.data;

        localStorage.setItem('token', access_token);
        setToken(access_token);
        setUser(userData);
    };

    const logout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                token,
                login,
                register,
                logout,
                isAuthenticated: !!token,
                loading,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
