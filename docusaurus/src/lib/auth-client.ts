/**
 * Better Auth Client Configuration
 *
 * This sets up Better Auth to work with our FastAPI backend.
 * Sessions are stored in the database and verified by the backend.
 */
import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
    baseURL: process.env.BACKEND_URL || "http://localhost:8000",
});

export const {
    signIn,
    signUp,
    signOut,
    useSession,
} = authClient;
