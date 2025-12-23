/**
 * User Profile Component
 *
 * Allows users to view and update their personalization settings.
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '@site/src/contexts/AuthContext';
import styles from './styles.module.css';

export default function UserProfile(): JSX.Element {
  const { user, updateProfile, isLoading } = useAuth();

  const [softwareLevel, setSoftwareLevel] = useState<string>(user?.software_background || '');
  const [hardwareLevel, setHardwareLevel] = useState<string>(user?.hardware_background || '');
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string>('');

  // Update form when user data changes
  useEffect(() => {
    if (user) {
      setSoftwareLevel(user.software_background || '');
      setHardwareLevel(user.hardware_background || '');
    }
  }, [user]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();

    setIsSaving(true);
    setSaveMessage('');

    try {
      await updateProfile(
        softwareLevel || undefined,
        hardwareLevel || undefined
      );
      setSaveMessage('Profile updated successfully!');

      // Clear message after 3 seconds
      setTimeout(() => setSaveMessage(''), 3000);
    } catch (error) {
      setSaveMessage('Failed to update profile. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  if (!user) {
    return (
      <div className={styles.container}>
        <p>Please log in to view your profile.</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.profileCard}>
        <h2 className={styles.title}>Your Profile</h2>

        <div className={styles.infoSection}>
          <label className={styles.label}>Email</label>
          <div className={styles.emailDisplay}>{user.email}</div>
        </div>

        <form onSubmit={handleSave} className={styles.form}>
          <h3 className={styles.sectionTitle}>Personalization Settings</h3>
          <p className={styles.sectionDescription}>
            Help us customize content to match your experience level
          </p>

          <div className={styles.formGroup}>
            <label htmlFor="software-level" className={styles.label}>
              Software/Programming Experience
            </label>
            <select
              id="software-level"
              value={softwareLevel}
              onChange={(e) => setSoftwareLevel(e.target.value)}
              className={styles.select}
            >
              <option value="">Select your level...</option>
              <option value="beginner">Beginner - New to programming</option>
              <option value="intermediate">Intermediate - Some programming experience</option>
              <option value="advanced">Advanced - Experienced programmer</option>
            </select>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="hardware-level" className={styles.label}>
              Hardware/Electronics Experience
            </label>
            <select
              id="hardware-level"
              value={hardwareLevel}
              onChange={(e) => setHardwareLevel(e.target.value)}
              className={styles.select}
            >
              <option value="">Select your level...</option>
              <option value="no_experience">No Experience - Never worked with hardware</option>
              <option value="hobbyist">Hobbyist - Some DIY projects</option>
              <option value="professional">Professional - Work with hardware regularly</option>
            </select>
          </div>

          <div className={styles.buttonGroup}>
            <button
              type="submit"
              disabled={isSaving || isLoading}
              className={styles.saveButton}
            >
              {isSaving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>

          {saveMessage && (
            <div className={saveMessage.includes('success') ? styles.successMessage : styles.errorMessage}>
              {saveMessage}
            </div>
          )}
        </form>

        <div className={styles.infoBox}>
          <h4>Why personalize?</h4>
          <p>
            By setting your experience level, the AI teaching assistant can:
          </p>
          <ul>
            <li>Adjust explanations to match your background</li>
            <li>Use appropriate terminology for your skill level</li>
            <li>Provide relevant examples based on your experience</li>
            <li>Suggest resources that match your learning needs</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
