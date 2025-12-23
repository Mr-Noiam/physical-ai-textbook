/**
 * ProtectedContent Component
 *
 * Wraps app content and requires authentication before displaying it.
 * Shows auth modal if user is not logged in.
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import AuthModal from '../AuthModal';
import styles from './styles.module.css';

interface ProtectedContentProps {
  children: React.ReactNode;
}

export default function ProtectedContent({ children }: ProtectedContentProps): JSX.Element {
  const { user, isLoading } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);

  useEffect(() => {
    // Show auth modal if not loading and no user
    if (!isLoading && !user) {
      setShowAuthModal(true);
    } else if (user) {
      setShowAuthModal(false);
    }
  }, [user, isLoading]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.loadingSpinner}>
          <div className={styles.spinner}></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // If user is not authenticated, show auth modal with backdrop
  if (!user) {
    return (
      <div className={styles.authRequired}>
        <div className={styles.authBackdrop}>
          <div className={styles.authMessage}>
            <h1>🔒 Authentication Required</h1>
            <p>Please sign in to access the Physical AI & Humanoid Robotics textbook.</p>
          </div>
        </div>
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => {
            // Don't allow closing if not authenticated
            // User must login/signup to access content
          }}
        />
      </div>
    );
  }

  // User is authenticated, show the content
  return <>{children}</>;
}
