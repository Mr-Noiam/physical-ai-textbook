/**
 * Reset Password Page
 *
 * Allows users to reset their password using a token from email.
 */

import React, { useState, useEffect } from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './reset-password.module.css';

export default function ResetPasswordPage(): JSX.Element {
  const { siteConfig } = useDocusaurusContext();
  const apiBaseUrl = (siteConfig.customFields?.apiBaseUrl as string) || 'http://localhost:8000';

  const [email, setEmail] = useState('');
  const [token, setToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState('');

  // Extract token and email from URL query parameters
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const tokenParam = urlParams.get('token');
    const emailParam = urlParams.get('email');

    if (tokenParam) setToken(tokenParam);
    if (emailParam) setEmail(emailParam);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');

    // Validation
    if (!email || !token || !newPassword || !confirmPassword) {
      setError('All fields are required');
      return;
    }

    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/auth/reset-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          reset_token: token,
          new_password: newPassword,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setIsSuccess(true);
        setMessage('Password reset successfully! You can now log in with your new password.');
        // Clear form
        setNewPassword('');
        setConfirmPassword('');
      } else {
        setError(data.detail || 'Failed to reset password. The link may have expired.');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout
      title="Reset Password"
      description="Reset your password for Physical AI Textbook"
    >
      <div className={styles.container}>
        <div className={styles.card}>
          <h1 className={styles.title}>🔐 Reset Password</h1>

          {isSuccess ? (
            <div className={styles.successBox}>
              <p className={styles.successMessage}>{message}</p>
              <Link to="/" className={styles.homeButton}>
                Go to Home Page
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className={styles.form}>
              <p className={styles.description}>
                Enter your new password below. Make sure it's at least 8 characters long.
              </p>

              {error && (
                <div className={styles.errorBox}>
                  {error}
                </div>
              )}

              {message && (
                <div className={styles.messageBox}>
                  {message}
                </div>
              )}

              <div className={styles.formGroup}>
                <label htmlFor="email" className={styles.label}>
                  Email
                </label>
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={styles.input}
                  placeholder="your.email@example.com"
                  required
                  disabled={!!email} // Disable if email is from URL
                />
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="newPassword" className={styles.label}>
                  New Password
                </label>
                <input
                  type="password"
                  id="newPassword"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className={styles.input}
                  placeholder="At least 8 characters"
                  required
                  minLength={8}
                />
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="confirmPassword" className={styles.label}>
                  Confirm New Password
                </label>
                <input
                  type="password"
                  id="confirmPassword"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className={styles.input}
                  placeholder="Re-enter your password"
                  required
                  minLength={8}
                />
              </div>

              {!token && (
                <div className={styles.warningBox}>
                  ⚠️ No reset token found. Please use the link from your email.
                </div>
              )}

              <button
                type="submit"
                disabled={isLoading || !token}
                className={styles.submitButton}
              >
                {isLoading ? 'Resetting Password...' : 'Reset Password'}
              </button>

              <div className={styles.linksContainer}>
                <Link to="/" className={styles.link}>
                  Back to Home
                </Link>
              </div>
            </form>
          )}
        </div>
      </div>
    </Layout>
  );
}
