/**
 * Profile Dropdown Component
 *
 * GitHub-style dropdown menu for user profile
 */
import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import styles from './styles.module.css';

interface ProfileDropdownProps {
    onSettingsClick: () => void;
}

export default function ProfileDropdown({ onSettingsClick }: ProfileDropdownProps) {
    const [isOpen, setIsOpen] = useState(false);
    const { user, signOut } = useAuth();
    const dropdownRef = useRef<HTMLDivElement>(null);

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        if (isOpen) {
            document.addEventListener('mousedown', handleClickOutside);
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [isOpen]);

    const handleSignOut = async () => {
        await signOut();
        setIsOpen(false);
    };

    const handleSettings = () => {
        onSettingsClick();
        setIsOpen(false);
    };

    if (!user) return null;

    // Get user initials for avatar
    const getInitials = () => {
        if (user.name) {
            const names = user.name.split(' ');
            if (names.length >= 2) {
                return `${names[0][0]}${names[1][0]}`.toUpperCase();
            }
            return user.name.substring(0, 2).toUpperCase();
        }
        return user.email.substring(0, 2).toUpperCase();
    };

    return (
        <div className={styles.profileDropdown} ref={dropdownRef}>
            <button
                className={styles.avatarButton}
                onClick={() => setIsOpen(!isOpen)}
                aria-label="User menu"
            >
                <div className={styles.avatar}>
                    {getInitials()}
                </div>
                <svg
                    className={`${styles.chevron} ${isOpen ? styles.chevronOpen : ''}`}
                    width="12"
                    height="12"
                    viewBox="0 0 12 12"
                    fill="currentColor"
                >
                    <path d="M6 9L1 4h10L6 9z" />
                </svg>
            </button>

            {isOpen && (
                <div className={styles.dropdownMenu}>
                    <div className={styles.userInfo}>
                        <div className={styles.userName}>{user.name}</div>
                        <div className={styles.userEmail}>{user.email}</div>
                    </div>

                    <div className={styles.divider} />

                    <div className={styles.skillLevels}>
                        <div className={styles.skillItem}>
                            <span className={styles.skillIcon}>💻</span>
                            <span className={styles.skillLabel}>
                                {user.software_background || 'intermediate'}
                            </span>
                        </div>
                        <div className={styles.skillItem}>
                            <span className={styles.skillIcon}>🔧</span>
                            <span className={styles.skillLabel}>
                                {user.hardware_background?.replace('_', ' ') || 'hobbyist'}
                            </span>
                        </div>
                    </div>

                    <div className={styles.divider} />

                    <button className={styles.menuItem} onClick={handleSettings}>
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M8 0a8 8 0 1 1 0 16A8 8 0 0 1 8 0zM1.5 8a6.5 6.5 0 1 0 13 0 6.5 6.5 0 0 0-13 0z" />
                            <path d="M8 3.5a.5.5 0 0 1 .5.5v4a.5.5 0 0 1-1 0V4a.5.5 0 0 1 .5-.5zM7.5 9a.5.5 0 0 0 0 1h1a.5.5 0 0 0 0-1h-1z" />
                        </svg>
                        Settings
                    </button>

                    <button className={styles.menuItem} onClick={handleSignOut}>
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M10 3.5a.5.5 0 0 0-.5-.5h-8a.5.5 0 0 0-.5.5v9a.5.5 0 0 0 .5.5h8a.5.5 0 0 0 .5-.5v-2a.5.5 0 0 1 1 0v2A1.5 1.5 0 0 1 9.5 14h-8A1.5 1.5 0 0 1 0 12.5v-9A1.5 1.5 0 0 1 1.5 2h8A1.5 1.5 0 0 1 11 3.5v2a.5.5 0 0 1-1 0v-2z" />
                            <path d="M15.854 8.354a.5.5 0 0 0 0-.708l-3-3a.5.5 0 0 0-.708.708L14.293 7.5H5.5a.5.5 0 0 0 0 1h8.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3z" />
                        </svg>
                        Sign Out
                    </button>
                </div>
            )}
        </div>
    );
}
