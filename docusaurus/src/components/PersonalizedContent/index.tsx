/**
 * Personalized Content Component
 *
 * Shows different content based on user's software/hardware background
 */
import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import styles from './styles.module.css';

interface PersonalizedContentProps {
    beginner?: React.ReactNode;
    intermediate?: React.ReactNode;
    advanced?: React.ReactNode;
    type?: 'software' | 'hardware';
}

export default function PersonalizedContent({
    beginner,
    intermediate,
    advanced,
    type = 'software'
}: PersonalizedContentProps) {
    const { user } = useAuth();

    // If user not logged in, show intermediate by default
    if (!user) {
        return <>{intermediate || beginner || advanced}</>;
    }

    // Get user's background level
    const userLevel = type === 'software'
        ? user.software_background
        : user.hardware_background;

    // Show appropriate content based on user level
    switch (userLevel) {
        case 'beginner':
        case 'no_experience':
            return beginner ? (
                <div className={styles.personalizedContent} data-level="beginner">
                    <div className={styles.levelBadge}>📚 Beginner Level</div>
                    {beginner}
                </div>
            ) : <>{intermediate || advanced}</>;

        case 'intermediate':
        case 'hobbyist':
            return intermediate ? (
                <div className={styles.personalizedContent} data-level="intermediate">
                    <div className={styles.levelBadge}>🎯 Intermediate Level</div>
                    {intermediate}
                </div>
            ) : <>{beginner || advanced}</>;

        case 'advanced':
        case 'professional':
            return advanced ? (
                <div className={styles.personalizedContent} data-level="advanced">
                    <div className={styles.levelBadge}>🚀 Advanced Level</div>
                    {advanced}
                </div>
            ) : <>{intermediate || beginner}</>;

        default:
            return <>{intermediate || beginner || advanced}</>;
    }
}
