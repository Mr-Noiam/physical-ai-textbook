/**
 * Authentication Modal
 *
 * Login/Signup modal for user authentication.
 */

import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import styles from './styles.module.css';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function AuthModal({ isOpen, onClose }: AuthModalProps): JSX.Element {
  const { login, signup, isLoading, error } = useAuth();
  const [mode, setMode] = useState<'login' | 'signup'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [softwareBackground, setSoftwareBackground] = useState('');
  const [hardwareBackground, setHardwareBackground] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      if (mode === 'login') {
        await login(email, password);
      } else {
        await signup(email, password, softwareBackground, hardwareBackground);
      }
      onClose();
      // Reset form
      setEmail('');
      setPassword('');
      setSoftwareBackground('');
      setHardwareBackground('');
    } catch (err) {
      // Error is handled in AuthContext
    }
  };

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <button className={styles.closeButton} onClick={onClose}>
          ✕
        </button>

        <h2>{mode === 'login' ? 'Login' : 'Sign Up'}</h2>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.formGroup}>
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="your@email.com"
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              placeholder="Minimum 8 characters"
            />
          </div>

          {mode === 'signup' && (
            <>
              <div className={styles.formGroup}>
                <label htmlFor="software">Software Background (Optional)</label>
                <select
                  id="software"
                  value={softwareBackground}
                  onChange={(e) => setSoftwareBackground(e.target.value)}
                >
                  <option value="">Select level...</option>
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="hardware">Hardware Background (Optional)</label>
                <select
                  id="hardware"
                  value={hardwareBackground}
                  onChange={(e) => setHardwareBackground(e.target.value)}
                >
                  <option value="">Select level...</option>
                  <option value="no_experience">No Experience</option>
                  <option value="hobbyist">Hobbyist</option>
                  <option value="professional">Professional</option>
                </select>
              </div>
            </>
          )}

          {error && <div className={styles.error}>{error}</div>}

          <button type="submit" className={styles.submitButton} disabled={isLoading}>
            {isLoading ? 'Please wait...' : mode === 'login' ? 'Login' : 'Sign Up'}
          </button>
        </form>

        <div className={styles.switchMode}>
          {mode === 'login' ? (
            <p>
              Don't have an account?{' '}
              <button onClick={() => setMode('signup')}>Sign up</button>
            </p>
          ) : (
            <p>
              Already have an account?{' '}
              <button onClick={() => setMode('login')}>Login</button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
