/**
 * Auth Client
 *
 * Simple auth client that calls our FastAPI backend.
 * Sessions are stored in the database and verified by the backend.
 */
import { useState, useEffect } from 'react';

// Backend URL configuration
// For development: http://localhost:8000
// For production: Update this to your deployed backend URL
const API_URL = typeof window !== 'undefined' && window.location.hostname === 'localhost'
    ? "http://localhost:8000"
    : "http://localhost:8000"; // TODO: Replace with deployed backend URL

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

interface SignUpData {
    email: string;
    password: string;
    name: string;
    software_background?: string;
    hardware_background?: string;
}

interface SignInData {
    email: string;
    password: string;
}

// Sign up function
export async function signUp(data: SignUpData) {
    const response = await fetch(`${API_URL}/api/v1/auth/signup`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include', // Important: include cookies
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Signup failed');
    }

    return response.json();
}

// Sign in function
export async function signIn(data: SignInData) {
    const response = await fetch(`${API_URL}/api/v1/auth/signin`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include', // Important: include cookies
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Sign in failed');
    }

    return response.json();
}

// Sign out function
export async function signOut() {
    const response = await fetch(`${API_URL}/api/v1/auth/signout`, {
        method: 'POST',
        credentials: 'include',
    });

    if (!response.ok) {
        throw new Error('Sign out failed');
    }

    return response.json();
}

// Get session function
async function getSession(): Promise<{ user: User | null; session: Session | null }> {
    try {
        const response = await fetch(`${API_URL}/api/v1/auth/session`, {
            credentials: 'include',
        });

        if (!response.ok) {
            return { user: null, session: null };
        }

        return response.json();
    } catch (error) {
        console.error('Error fetching session:', error);
        return { user: null, session: null };
    }
}

// React hook to use session
export function useSession() {
    const [data, setData] = useState<{ user: User | null; session: Session | null } | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        getSession().then((sessionData) => {
            setData(sessionData);
            setIsLoading(false);
        });
    }, []);

    return { data, isLoading };
}
