/**
 * Language Selector Component
 *
 * Allows users to select a language and translate content
 * Supports 15 languages with proper RTL rendering for Urdu/Arabic
 */

import React, { useState, useEffect } from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './styles.module.css';

// Supported languages from backend
const SUPPORTED_LANGUAGES = {
  en: { name: 'English', flag: '🇬🇧', rtl: false },
  ur: { name: 'اردو (Urdu)', flag: '🇵🇰', rtl: true },
  ar: { name: 'العربية (Arabic)', flag: '🇸🇦', rtl: true },
  hi: { name: 'हिंदी (Hindi)', flag: '🇮🇳', rtl: false },
  es: { name: 'Español', flag: '🇪🇸', rtl: false },
  fr: { name: 'Français', flag: '🇫🇷', rtl: false },
  de: { name: 'Deutsch', flag: '🇩🇪', rtl: false },
  zh: { name: '中文 (Chinese)', flag: '🇨🇳', rtl: false },
  ja: { name: '日本語 (Japanese)', flag: '🇯🇵', rtl: false },
  ko: { name: '한국어 (Korean)', flag: '🇰🇷', rtl: false },
  pt: { name: 'Português', flag: '🇵🇹', rtl: false },
  ru: { name: 'Русский (Russian)', flag: '🇷🇺', rtl: false },
  tr: { name: 'Türkçe (Turkish)', flag: '🇹🇷', rtl: false },
  vi: { name: 'Tiếng Việt', flag: '🇻🇳', rtl: false },
  th: { name: 'ไทย (Thai)', flag: '🇹🇭', rtl: false },
  id: { name: 'Bahasa Indonesia', flag: '🇮🇩', rtl: false },
};

export default function LanguageSelector(): JSX.Element {
  const { siteConfig } = useDocusaurusContext();
  const apiBaseUrl = (siteConfig.customFields?.apiBaseUrl as string) || 'http://localhost:8000';

  const [selectedLanguage, setSelectedLanguage] = useState<string>('en');
  const [isOpen, setIsOpen] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);

  // Handle language selection
  const handleLanguageSelect = async (langCode: string) => {
    if (langCode === 'en') {
      // Reset to original English
      setSelectedLanguage('en');
      setIsOpen(false);

      // Dispatch event to reset content
      window.dispatchEvent(new CustomEvent('languageChange', {
        detail: { language: 'en', translated: false }
      }));
      return;
    }

    setSelectedLanguage(langCode);
    setIsOpen(false);
    setIsTranslating(true);

    try {
      // Get all text content from the page
      const mainContent = document.querySelector('article.markdown') ||
                          document.querySelector('main');

      if (!mainContent) {
        console.warn('No content to translate found');
        setIsTranslating(false);
        return;
      }

      // Extract text paragraphs for translation
      const paragraphs = mainContent.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li');
      const textsToTranslate: string[] = [];

      paragraphs.forEach((p) => {
        const text = p.textContent?.trim();
        if (text && text.length > 0) {
          textsToTranslate.push(text);
        }
      });

      if (textsToTranslate.length === 0) {
        console.warn('No text content found to translate');
        setIsTranslating(false);
        return;
      }

      // Translate using backend API (batch translation)
      const response = await fetch(`${apiBaseUrl}/api/v1/translate/multiple`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contents: textsToTranslate,
          target_language: langCode,
          source_language: 'en',
        }),
      });

      if (!response.ok) {
        throw new Error(`Translation failed: ${response.statusText}`);
      }

      const data = await response.json();

      // Apply translations to the page
      const isRTL = SUPPORTED_LANGUAGES[langCode]?.rtl || false;
      let index = 0;

      paragraphs.forEach((p) => {
        const text = p.textContent?.trim();
        if (text && text.length > 0 && index < data.translations.length) {
          const translation = data.translations[index];
          p.textContent = translation.translated_content;

          // Apply RTL styling if needed
          if (isRTL) {
            (p as HTMLElement).style.direction = 'rtl';
            (p as HTMLElement).style.textAlign = 'right';
            (p as HTMLElement).style.fontFamily = "'Noto Nastaliq Urdu', 'Arabic Typesetting', Arial, sans-serif";
          }

          index++;
        }
      });

      // Dispatch event for other components that might need to know
      window.dispatchEvent(new CustomEvent('languageChange', {
        detail: {
          language: langCode,
          translated: true,
          rtl: isRTL,
          cachedCount: data.cached_count || 0,
          total: data.total || 0
        }
      }));

      console.log(`Translation complete: ${data.cached_count}/${data.total} from cache`);

    } catch (error) {
      console.error('Translation error:', error);
      alert('Translation failed. Please try again.');
    } finally {
      setIsTranslating(false);
    }
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest(`.${styles.languageSelector}`)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('click', handleClickOutside);
    }

    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, [isOpen]);

  const currentLang = SUPPORTED_LANGUAGES[selectedLanguage];

  return (
    <div className={styles.languageSelector}>
      <button
        className={styles.selectorButton}
        onClick={() => setIsOpen(!isOpen)}
        disabled={isTranslating}
        aria-label="Select language"
      >
        <span className={styles.flag}>{currentLang.flag}</span>
        <span className={styles.langCode}>{selectedLanguage.toUpperCase()}</span>
        {isTranslating && <span className={styles.spinner}>⟳</span>}
        {!isTranslating && <span className={styles.arrow}>▼</span>}
      </button>

      {isOpen && (
        <div className={styles.dropdown}>
          <div className={styles.dropdownHeader}>
            <span>🌍 Select Language</span>
            <span className={styles.badge}>15 languages</span>
          </div>

          <div className={styles.languageList}>
            {Object.entries(SUPPORTED_LANGUAGES).map(([code, lang]) => (
              <button
                key={code}
                className={`${styles.languageItem} ${code === selectedLanguage ? styles.active : ''}`}
                onClick={() => handleLanguageSelect(code)}
              >
                <span className={styles.flag}>{lang.flag}</span>
                <span className={styles.langName}>{lang.name}</span>
                {code === 'en' && <span className={styles.originalBadge}>Original</span>}
                {code === selectedLanguage && code !== 'en' && <span className={styles.activeBadge}>✓</span>}
              </button>
            ))}
          </div>

          <div className={styles.dropdownFooter}>
            <small>💡 Powered by Gemini AI (FREE)</small>
          </div>
        </div>
      )}
    </div>
  );
}
