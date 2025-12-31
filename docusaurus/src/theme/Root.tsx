/**
 * Root Component
 *
 * Wraps the entire Docusaurus app.
 * Used to inject global components like the ChatbotWidget and AuthProvider.
 *
 * See: https://docusaurus.io/docs/swizzling#wrapper-your-site-with-root
 */

import React from 'react';
import ChatbotWidget from '@site/src/components/ChatbotWidget';
import ErrorBoundary from '@site/src/components/ErrorBoundary';
import { AuthProvider } from '@site/src/contexts/AuthContext';

export default function Root({ children }): JSX.Element {
  return (
    <AuthProvider>
      {children}
      <ErrorBoundary>
        <ChatbotWidget />
      </ErrorBoundary>
    </AuthProvider>
  );
}
