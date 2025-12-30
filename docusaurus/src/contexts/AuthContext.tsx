/**
 * Auth Context Provider
 *
 * Provides global authentication state management.
 * Allows any component to access user data and refresh session.
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
    id: string;
    email: string;
    name: string;
    software_background?: string;
    hardware_background?: string;
}

interface Session {
    id: string;
    expires_at: string;
}

interface AuthContextType {
    user: User | null;
    session: Session | null;
    isLoading: boolean;
    refreshSession: () => Promise<void>;
    signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_URL = typeof window !== 'undefined' && window.location.hostname === 'localhost'
    ? "http://localhost:8000"
    : "https://physical-ai-textbook-production-d71f.up.railway.app";

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [session, setSession] = useState<Session | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    const refreshSession = async () => {
        try {
            setIsLoading(true);
            const response = await fetch(`${API_URL}/api/v1/auth/session`, {
                credentials: 'include',
            });

            if (response.ok) {
                const data = await response.json();
                setUser(data.user);
                setSession(data.session);
            } else {
                setUser(null);
                setSession(null);
            }
        } catch (error) {
            console.error('Error fetching session:', error);
            setUser(null);
            setSession(null);
        } finally {
            setIsLoading(false);
        }
    };

    const signOut = async () => {
        try {
            await fetch(`${API_URL}/api/v1/auth/signout`, {
                method: 'POST',
                credentials: 'include',
            });
            setUser(null);
            setSession(null);
        } catch (error) {
            console.error('Sign out error:', error);
        }
    };

    useEffect(() => {
        refreshSession();
    }, []);

    return (
        <AuthContext.Provider value={{ user, session, isLoading, refreshSession, signOut }}>
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
