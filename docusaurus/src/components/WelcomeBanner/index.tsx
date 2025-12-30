/**
 * Welcome Banner Component
 *
 * Shows personalized welcome message based on user profile
 */
import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import styles from './styles.module.css';

export default function WelcomeBanner() {
    const { user, isLoading } = useAuth();

    if (isLoading) {
        return null;
    }

    if (!user) {
        return (
            <div className={styles.banner} data-type="guest">
                <h2>👋 Welcome to Physical AI & Humanoid Robotics!</h2>
                <p>
                    Sign in to get personalized content based on your experience level.
                    Content will adapt to your software and hardware background!
                </p>
            </div>
        );
    }

    // Get personalized greeting based on background
    const getSoftwareGreeting = () => {
        switch (user.software_background) {
            case 'beginner':
                return "We'll start with fundamentals and build up your programming skills step by step.";
            case 'intermediate':
                return "You have a solid foundation! We'll dive into robotics-specific programming patterns.";
            case 'advanced':
                return "With your advanced skills, we'll focus on architecture and best practices.";
            default:
                return "Let's explore Physical AI together!";
        }
    };

    const getHardwareGreeting = () => {
        switch (user.hardware_background) {
            case 'no_experience':
                return "Don't worry - we'll introduce hardware concepts from scratch.";
            case 'hobbyist':
                return "Your hands-on experience will be valuable as we build complex systems!";
            case 'professional':
                return "Your professional expertise will help you master humanoid robotics quickly.";
            default:
                return "";
        }
    };

    return (
        <div className={styles.banner} data-type="personalized">
            <h2>👋 Welcome back, {user.name}!</h2>
            <p className={styles.greeting}>
                <strong>Software:</strong> {getSoftwareGreeting()}
            </p>
            <p className={styles.greeting}>
                <strong>Hardware:</strong> {getHardwareGreeting()}
            </p>
            <div className={styles.badges}>
                <span className={styles.badge}>
                    💻 {user.software_background || 'intermediate'}
                </span>
                <span className={styles.badge}>
                    🔧 {user.hardware_background?.replace('_', ' ') || 'hobbyist'}
                </span>
            </div>
        </div>
    );
}
