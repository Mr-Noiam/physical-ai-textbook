/**
 * Root Component
 *
 * Wraps the entire Docusaurus app.
 * Used to inject global components like the ChatbotWidget.
 *
 * See: https://docusaurus.io/docs/swizzling#wrapper-your-site-with-root
 */

import React from 'react';
import ChatbotWidget from '@site/src/components/ChatbotWidget';

export default function Root({ children }): JSX.Element {
  return (
    <>
      {children}
      <ChatbotWidget />
    </>
  );
}
