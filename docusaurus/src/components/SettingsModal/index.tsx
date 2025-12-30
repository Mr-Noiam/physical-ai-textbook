/**
 * Settings Modal Component
 *
 * Allows users to update their profile settings
 */
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import styles from './styles.module.css';

interface SettingsModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const API_URL = typeof window !== 'undefined' && window.location.hostname === 'localhost'
    ? "http://localhost:8000"
    : "https://physical-ai-textbook-production-d71f.up.railway.app";

export default function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
    const { user, refreshSession } = useAuth();
    const [name, setName] = useState('');
    const [softwareBackground, setSoftwareBackground] = useState('intermediate');
    const [hardwareBackground, setHardwareBackground] = useState('hobbyist');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [loading, setLoading] = useState(false);

    // Initialize form with user data
    useEffect(() => {
        if (user) {
            setName(user.name || '');
            setSoftwareBackground(user.software_background || 'intermediate');
            setHardwareBackground(user.hardware_background || 'hobbyist');
        }
    }, [user]);

    if (!isOpen || !user) return null;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setLoading(true);

        try {
            const response = await fetch(`${API_URL}/api/v1/auth/update-profile`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    name,
                    software_background: softwareBackground,
                    hardware_background: hardwareBackground,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to update profile');
            }

            // Refresh session to get updated user data
            await refreshSession();
            setSuccess('Profile updated successfully!');

            // Close modal after 1.5 seconds
            setTimeout(() => {
                onClose();
                setSuccess('');
            }, 1500);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to update profile');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.modalOverlay} onClick={onClose}>
            <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
                <div className={styles.modalHeader}>
                    <h2>Settings</h2>
                    <button className={styles.closeButton} onClick={onClose}>
                        ×
                    </button>
                </div>

                {error && <div className={styles.error}>{error}</div>}
                {success && <div className={styles.success}>{success}</div>}

                <form onSubmit={handleSubmit}>
                    <div className={styles.section}>
                        <h3>Profile Information</h3>

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

                        <div className={styles.formGroup}>
                            <label htmlFor="email">Email</label>
                            <input
                                type="email"
                                id="email"
                                value={user.email}
                                disabled
                                className={styles.disabledInput}
                            />
                            <p className={styles.helpText}>Email cannot be changed</p>
                        </div>
                    </div>

                    <div className={styles.section}>
                        <h3>Experience Levels</h3>
                        <p className={styles.sectionDescription}>
                            Content will be personalized based on your experience levels
                        </p>

                        <div className={styles.formGroup}>
                            <label htmlFor="software">
                                💻 Programming Experience
                            </label>
                            <select
                                id="software"
                                value={softwareBackground}
                                onChange={(e) => setSoftwareBackground(e.target.value)}
                            >
                                <option value="beginner">Beginner - New to programming</option>
                                <option value="intermediate">Intermediate - Comfortable with Python</option>
                                <option value="advanced">Advanced - Expert programmer</option>
                            </select>
                        </div>

                        <div className={styles.formGroup}>
                            <label htmlFor="hardware">
                                🔧 Hardware Experience
                            </label>
                            <select
                                id="hardware"
                                value={hardwareBackground}
                                onChange={(e) => setHardwareBackground(e.target.value)}
                            >
                                <option value="no_experience">No Experience - New to hardware</option>
                                <option value="hobbyist">Hobbyist - Some DIY projects</option>
                                <option value="professional">Professional - Industry experience</option>
                            </select>
                        </div>
                    </div>

                    <div className={styles.modalFooter}>
                        <button
                            type="button"
                            onClick={onClose}
                            className={styles.cancelButton}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className={styles.saveButton}
                            disabled={loading}
                        >
                            {loading ? 'Saving...' : 'Save Changes'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
