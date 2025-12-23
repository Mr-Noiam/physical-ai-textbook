/**
 * UserMenu Component
 *
 * Displays user info and logout button in the navbar.
 * Shows login/signup button when user is not authenticated.
 */

import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import AuthModal from '../AuthModal';
import styles from './styles.module.css';

export default function UserMenu(): JSX.Element {
  const { user, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  // If user is not authenticated, show login/signup button
  if (!user) {
    return (
      <>
        <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
        <button
          className={styles.authButton}
          onClick={() => setShowAuthModal(true)}
          aria-label="Login or Sign up"
        >
          <span className={styles.authIcon}>🔐</span>
          <span className={styles.authText}>Login / Sign Up</span>
        </button>
      </>
    );
  }

  const handleLogout = () => {
    logout();
    setIsOpen(false);
  };

  return (
    <div className={styles.userMenu} ref={menuRef}>
      <button
        className={styles.userButton}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="User menu"
      >
        <span className={styles.userIcon}>👤</span>
        <span className={styles.userEmail}>{user.email}</span>
        <span className={styles.dropdownIcon}>{isOpen ? '▲' : '▼'}</span>
      </button>

      {isOpen && (
        <div className={styles.dropdown}>
          <div className={styles.userInfo}>
            <div className={styles.infoRow}>
              <strong>Email:</strong> {user.email}
            </div>
            {user.software_background && (
              <div className={styles.infoRow}>
                <strong>Software:</strong> {user.software_background}
              </div>
            )}
            {user.hardware_background && (
              <div className={styles.infoRow}>
                <strong>Hardware:</strong> {user.hardware_background}
              </div>
            )}
          </div>
          <div className={styles.menuActions}>
            <a href="/profile" className={styles.profileLink}>
              ⚙️ Profile Settings
            </a>
            <button className={styles.logoutButton} onClick={handleLogout}>
              🚪 Logout
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
