/**
 * Authentication Modal Component
 *
 * Provides signup and signin forms for users.
 * Uses Better Auth for authentication.
 */
import React, { useState } from 'react';
import { signIn, signUp, useSession } from '../../lib/auth-client';
import styles from './styles.module.css';

interface AuthModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export default function AuthModal({ isOpen, onClose }: AuthModalProps) {
    const [mode, setMode] = useState<'signin' | 'signup'>('signin');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [name, setName] = useState('');
    const [softwareBackground, setSoftwareBackground] = useState('intermediate');
    const [hardwareBackground, setHardwareBackground] = useState('hobbyist');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    if (!isOpen) return null;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            if (mode === 'signup') {
                await signUp({
                    email,
                    password,
                    name,
                    software_background: softwareBackground,
                    hardware_background: hardwareBackground,
                });
                onClose();
                window.location.reload(); // Refresh to show logged-in state
            } else {
                await signIn({
                    email,
                    password,
                });
                onClose();
                window.location.reload();
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Authentication failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.modalOverlay} onClick={onClose}>
            <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
                <button className={styles.closeButton} onClick={onClose}>
                    ×
                </button>

                <h2>{mode === 'signin' ? 'Sign In' : 'Create Account'}</h2>

                {error && <div className={styles.error}>{error}</div>}

                <form onSubmit={handleSubmit}>
                    {mode === 'signup' && (
                        <div className={styles.formGroup}>
                            <label htmlFor="name">Name</label>
                            <input
                                type="text"
                                id="name"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                required
                            />
                        </div>
                    )}

                    <div className={styles.formGroup}>
                        <label htmlFor="email">Email</label>
                        <input
                            type="email"
                            id="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>

                    <div className={styles.formGroup}>
                        <label htmlFor="password">Password</label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            minLength={8}
                        />
                    </div>

                    {mode === 'signup' && (
                        <>
                            <div className={styles.formGroup}>
                                <label htmlFor="software">Programming Experience</label>
                                <select
                                    id="software"
                                    value={softwareBackground}
                                    onChange={(e) => setSoftwareBackground(e.target.value)}
                                >
                                    <option value="beginner">Beginner</option>
                                    <option value="intermediate">Intermediate</option>
                                    <option value="advanced">Advanced</option>
                                </select>
                            </div>

                            <div className={styles.formGroup}>
                                <label htmlFor="hardware">Hardware Experience</label>
                                <select
                                    id="hardware"
                                    value={hardwareBackground}
                                    onChange={(e) => setHardwareBackground(e.target.value)}
                                >
                                    <option value="no_experience">No Experience</option>
                                    <option value="hobbyist">Hobbyist</option>
                                    <option value="professional">Professional</option>
                                </select>
                            </div>
                        </>
                    )}

                    <button
                        type="submit"
                        className={styles.submitButton}
                        disabled={loading}
                    >
                        {loading ? 'Loading...' : mode === 'signin' ? 'Sign In' : 'Sign Up'}
                    </button>
                </form>

                <div className={styles.switchMode}>
                    {mode === 'signin' ? (
                        <p>
                            Don't have an account?{' '}
                            <button onClick={() => setMode('signup')}>Sign Up</button>
                        </p>
                    ) : (
                        <p>
                            Already have an account?{' '}
                            <button onClick={() => setMode('signin')}>Sign In</button>
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
}
