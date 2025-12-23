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
import { useAuth } from '../../contexts/AuthContext';
import AuthModal from '../AuthModal';
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
  const { siteConfig } = useDocusaurusContext();
  const API_BASE_URL = (siteConfig.customFields?.apiBaseUrl as string) || 'http://localhost:8000';
  const { user, token, logout } = useAuth();

  const [isOpen, setIsOpen] = useState(false);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
    }
  }, [isOpen]);

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

    // Check if user is authenticated
    if (!user) {
      setIsAuthModalOpen(true);
      return;
    }

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
      // Call backend API
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      // Add auth token if user is logged in
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}/api/v1/chatbot/ask`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          question,
          selected_text: selectedContext || null,
          conversation_history: messages.map(m => ({
            role: m.role,
            content: m.content,
          })),
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
      <AuthModal isOpen={isAuthModalOpen} onClose={() => setIsAuthModalOpen(false)} />

      {/* Floating "Ask about this" button (appears on text selection) */}
      {selectedText && !isOpen && (
        <button
          className={styles.askSelectionButton}
          onClick={handleAskAboutSelection}
          title="Ask AI about selected text"
        >
          💡 Ask about this
        </button>
      )}

      {/* Main chat button */}
      <button
        className={`${styles.chatButton} ${isOpen ? styles.chatButtonOpen : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle chatbot"
      >
        {isOpen ? '✕' : '💬'}
      </button>

      {/* Chat window */}
      {isOpen && (
        <div className={styles.chatWindow}>
          {/* Header */}
          <div className={styles.chatHeader}>
            <div className={styles.chatTitle}>
              <span className={styles.chatIcon}>🤖</span>
              <span>AI Teaching Assistant</span>
            </div>
            <div className={styles.headerButtons}>
              {user ? (
                <div className={styles.userMenu}>
                  <span className={styles.userEmail}>{user.email}</span>
                  <button onClick={logout} className={styles.logoutButton}>
                    Logout
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setIsAuthModalOpen(true)}
                  className={styles.loginButton}
                >
                  Login
                </button>
              )}
              <button
                className={styles.clearButton}
                onClick={clearChat}
                title="Clear conversation"
              >
                🗑️
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className={styles.chatMessages}>
            {!user ? (
              <div className={styles.welcomeMessage}>
                <p>🔒 Login Required</p>
                <p>Please login or signup to use the AI teaching assistant.</p>
                <button
                  className={styles.loginButtonLarge}
                  onClick={() => setIsAuthModalOpen(true)}
                >
                  Login / Sign Up
                </button>
              </div>
            ) : messages.length === 0 ? (
              <div className={styles.welcomeMessage}>
                <p>👋 Hi! I'm your AI teaching assistant.</p>
                <p>Ask me anything about the textbook content:</p>
                <div className={styles.suggestionButtons}>
                  <button
                    className={styles.suggestionButton}
                    onClick={() => sendMessage("What is a ROS 2 node?")}
                  >
                    What is a ROS 2 node?
                  </button>
                  <button
                    className={styles.suggestionButton}
                    onClick={() => sendMessage("How do I create a URDF file?")}
                  >
                    How do I create a URDF file?
                  </button>
                  <button
                    className={styles.suggestionButton}
                    onClick={() => sendMessage("Explain Isaac Sim synthetic data")}
                  >
                    Explain Isaac Sim synthetic data
                  </button>
                </div>
                <p>You can also select text and ask about it!</p>
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
                      <div className={styles.sourcesTitle}>📚 Sources:</div>
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
              placeholder="Ask a question..."
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
