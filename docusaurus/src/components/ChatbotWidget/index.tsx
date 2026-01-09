/**
 * ChatbotWidget Component
 *
 * AI-powered textbook assistant with RAG (Retrieval-Augmented Generation).
 * Provides contextual help based on textbook content.
 *
 * Features:
 * - Floating chat button
 * - Expandable chat window
 * - Question answering with sources
 * - Text selection support ("Ask about this")
 * - Conversation history
 * - Mobile responsive
 */

import React, { useState, useRef, useEffect } from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Translate, { translate } from '@docusaurus/Translate';
import { useAuth } from '../../contexts/AuthContext';
import styles from './styles.module.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  timestamp: Date;
}

interface Source {
  file: string;
  section: string;
  url: string;
}

export default function ChatbotWidget(): JSX.Element {
  const { siteConfig, i18n } = useDocusaurusContext();
  const API_BASE_URL = (siteConfig.customFields?.apiBaseUrl as string) || 'http://localhost:8000';
  const { currentLocale } = i18n;
  const { user } = useAuth();

  // Detect RTL languages
  const isRTL = currentLocale === 'ur'; // Urdu is RTL

  // Translated suggestion questions
  const suggestion1Text = translate({
    id: 'chatbot.suggestion1',
    message: 'What is a ROS 2 node?',
    description: 'Chatbot suggestion 1'
  });
  const suggestion2Text = translate({
    id: 'chatbot.suggestion2',
    message: 'How do I create a URDF file?',
    description: 'Chatbot suggestion 2'
  });
  const suggestion3Text = translate({
    id: 'chatbot.suggestion3',
    message: 'Explain Isaac Sim synthetic data',
    description: 'Chatbot suggestion 3'
  });

  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const chatWindowRef = useRef<HTMLDivElement>(null);
  const chatButtonRef = useRef<HTMLButtonElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Combined effect for handling side-effects when chat is open
  useEffect(() => {
    // 1. Define the click handler
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Node;
      // If the click is outside the window and button, close the chat
      if (
        chatWindowRef.current &&
        !chatWindowRef.current.contains(target) &&
        chatButtonRef.current &&
        !chatButtonRef.current.contains(target)
      ) {
        setIsOpen(false);
      }
    };

    // 2. Add listener and focus input if chat is open
    if (isOpen) {
      inputRef.current?.focus();
      document.addEventListener('mousedown', handleClickOutside);
    }

    // 3. Cleanup function to remove listener
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]); // This effect depends only on the `isOpen` state

  // Handle text selection
  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection();
      const text = selection?.toString().trim();

      if (text && text.length > 10) {
        setSelectedText(text);
      }
    };

    document.addEventListener('mouseup', handleSelection);
    return () => document.removeEventListener('mouseup', handleSelection);
  }, []);

  const sendMessage = async (question: string, selectedContext?: string) => {
    if (!question.trim()) return;

    // Add user message to chat
    const userMessage: Message = {
      role: 'user',
      content: question,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Call backend API with credentials for authenticated users
      const response = await fetch(`${API_BASE_URL}/api/v1/chatbot/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Send cookies for authentication
        body: JSON.stringify({
          question,
          selected_text: selectedContext || null,
          conversation_history: messages.map(m => ({
            role: m.role,
            content: m.content,
          })),
          language: currentLocale, // Send current locale to backend
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Add assistant message to chat
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error('Error calling chatbot API:', error);

      // Show error message
      const errorMessage: Message = {
        role: 'assistant',
        content: '❌ Sorry, I encountered an error. Please make sure the backend server is running and try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setSelectedText(''); // Clear selection after use
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleAskAboutSelection = () => {
    if (selectedText) {
      const question = `Explain this: "${selectedText.slice(0, 100)}${selectedText.length > 100 ? '...' : ''}"`;
      setIsOpen(true);
      sendMessage(question, selectedText);
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <>
      {/* Floating "Ask about this" button (appears on text selection) */}
      {selectedText && !isOpen && (
        <button
          className={styles.askSelectionButton}
          onClick={handleAskAboutSelection}
          title={translate({
            id: 'chatbot.askAboutSelectionButtonTitle',
            message: 'Ask AI about selected text',
            description: 'Title for the "Ask about this" button',
          })}
        >
          💡{' '}
          <Translate id="chatbot.askAboutSelectionButton" description="Ask about this button text">
            Ask about this
          </Translate>
        </button>
      )}

      {/* Main chat button */}
      <button
        ref={chatButtonRef}
        className={`${styles.chatButton} ${isOpen ? styles.chatButtonOpen : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        aria-label={translate({
          id: 'chatbot.toggleChatbotAriaLabel',
          message: 'Toggle chatbot',
          description: 'ARIA label for the chatbot toggle button',
        })}
      >
        {isOpen ? '✕' : '💬'}
      </button>

      {/* Chat window */}
      {isOpen && (
        <div ref={chatWindowRef} className={`${styles.chatWindow} ${isRTL ? styles.chatWindowRTL : ''}`} dir={isRTL ? 'rtl' : 'ltr'}>
          {/* Header */}
          <div className={styles.chatHeader}>
            <div className={styles.chatTitle}>
              <span className={styles.chatIcon}>🤖</span>
              <span>
                <Translate
                  id="chatbot.headerTitle"
                  description="Chatbot header title"
                >
                  AI Teaching Assistant
                </Translate>
              </span>
              {user && <span className={styles.userBadge}>{user.name}</span>}
            </div>
            <div className={styles.headerButtons}>
              <button
                className={styles.clearButton}
                onClick={clearChat}
                title={translate({
                  id: 'chatbot.clearConversationButtonTitle',
                  message: 'Clear conversation',
                  description: 'Title for the clear conversation button',
                })}
              >
                🗑️
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className={styles.chatMessages}>
            {messages.length === 0 ? (
              <div className={styles.welcomeMessage}>
                <p>
                  <Translate
                    id="chatbot.welcomeGreetingFull"
                    description="Chatbot welcome greeting with username"
                    values={{ username: user?.name || translate({
                      id: 'chatbot.defaultUsername',
                      message: 'there',
                      description: 'Default username when user is not logged in'
                    }) }}
                  >
                    {'👋 Hi, {username}! I\'m your AI teaching assistant.'}
                  </Translate>
                </p>
                <p>
                  <Translate id="chatbot.askPrompt" description="Prompt for asking questions">
                    Ask me anything about the textbook content:
                  </Translate>
                </p>
                {!user && (
                  <p className={styles.loginHint}>
                    💡{' '}
                    <em>
                      <Translate
                        id="chatbot.loginHint"
                        description="Hint for logging in"
                      >
                        Login to get personalized answers based on your experience level!
                      </Translate>
                    </em>
                  </p>
                )}
                <div className={styles.suggestionButtons}>
                  <button
                    className={styles.suggestionButton}
                    onClick={() => sendMessage(suggestion1Text)}
                  >
                    <Translate
                      id="chatbot.suggestion1"
                      description="Chatbot suggestion 1"
                    >
                      What is a ROS 2 node?
                    </Translate>
                  </button>
                  <button
                    className={styles.suggestionButton}
                    onClick={() => sendMessage(suggestion2Text)}
                  >
                    <Translate
                      id="chatbot.suggestion2"
                      description="Chatbot suggestion 2"
                    >
                      How do I create a URDF file?
                    </Translate>
                  </button>
                  <button
                    className={styles.suggestionButton}
                    onClick={() => sendMessage(suggestion3Text)}
                  >
                    <Translate
                      id="chatbot.suggestion3"
                      description="Chatbot suggestion 3"
                    >
                      Explain Isaac Sim synthetic data
                    </Translate>
                  </button>
                </div>
                <p>
                  <Translate id="chatbot.selectTextPrompt" description="Prompt for selecting text">
                    You can also select text and ask about it!
                  </Translate>
                </p>
              </div>
            ) : (
              messages.map((message, index) => (
                <div
                  key={index}
                  className={`${styles.message} ${
                    message.role === 'user' ? styles.userMessage : styles.assistantMessage
                  }`}
                >
                  <div className={styles.messageContent}>
                    {message.content}
                  </div>

                  {/* Sources */}
                  {message.sources && message.sources.length > 0 && (
                    <div className={styles.sources}>
                      <div className={styles.sourcesTitle}>
                        <Translate id="chatbot.sourcesTitle" description="Sources title">
                          📚 Sources:
                        </Translate>
                      </div>
                      {message.sources.map((source, idx) => (
                        <a
                          key={idx}
                          href={source.url}
                          className={styles.sourceLink}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          {source.section}
                        </a>
                      ))}
                    </div>
                  )}

                  <div className={styles.messageTime}>
                    {message.timestamp.toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </div>
                </div>
              ))
            )}

            {/* Loading indicator */}
            {isLoading && (
              <div className={`${styles.message} ${styles.assistantMessage}`}>
                <div className={styles.loadingDots}>
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <form onSubmit={handleSubmit} className={styles.chatInput}>
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={translate({
                id: 'chatbot.inputPlaceholder',
                message: 'Ask a question...',
                description: 'Placeholder for the chatbot input field',
              })}
              disabled={isLoading}
              className={styles.inputField}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className={styles.sendButton}
            >
              {isLoading ? '⏳' : '➤'}
            </button>
          </form>
        </div>
      )}
    </>
  );
}
