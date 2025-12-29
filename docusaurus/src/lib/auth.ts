/**
 * Better Auth Server Configuration
 *
 * This configures Better Auth to work with our PostgreSQL database.
 * It handles user authentication and session management.
 */
import { betterAuth } from "better-auth";
import { Pool } from "pg";

// Create PostgreSQL connection pool
const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: process.env.NODE_ENV === "production" ? { rejectUnauthorized: false } : undefined,
});

export const auth = betterAuth({
    database: pool as any,
    emailAndPassword: {
        enabled: true,
        requireEmailVerification: false, // Disable for MVP
    },
    user: {
        additionalFields: {
            software_background: {
                type: "string",
                required: false,
            },
            hardware_background: {
                type: "string",
                required: false,
            },
        },
    },
    session: {
        expiresIn: 60 * 60 * 24 * 7, // 7 days
        updateAge: 60 * 60 * 24, // 1 day
    },
});
