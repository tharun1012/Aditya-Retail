import React, { useState, useRef, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { MessageCircle, X, Send, Minimize2, Bot, Loader } from 'lucide-react';

const AIChatWidget = () => {
  const [isOpen, setIsOpen] = useState(() => {
    return localStorage.getItem('ai_chat_open') === 'true';
  });
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState(() => {
    const savedMessages = localStorage.getItem('ai_chat_messages');
    if (savedMessages) {
      try {
        const parsed = JSON.parse(savedMessages);
        // Convert timestamp strings back to Date objects
        return parsed.map(msg => ({
          ...msg,
          timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date()
        }));
      } catch (error) {
        console.error('Error parsing saved messages:', error);
        localStorage.removeItem('ai_chat_messages');
      }
    }
    return [
      {
        role: 'assistant',
        content: 'Hi! 👋 I\'m your AI Shopping Assistant. How can I help you find the perfect appliance today?',
        timestamp: new Date()
      }
    ];
  });
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  
  // Check if mobile device
  const [isMobile, setIsMobile] = useState(false);
  
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Persist chat state
  useEffect(() => {
    localStorage.setItem('ai_chat_messages', JSON.stringify(messages));
  }, [messages]);

  useEffect(() => {
    localStorage.setItem('ai_chat_open', isOpen);
  }, [isOpen]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Convert markdown links to clickable HTML
  const renderMessageContent = (content) => {
    try {
      if (!content || typeof content !== 'string') {
        return content;
      }

      // First, convert any full URLs to relative URLs
      let processedContent = content;
      
      // Convert full product URLs to relative hash URLs
      // This catches any domain (preview, live, etc.) and converts to relative
      processedContent = processedContent.replace(
        /https?:\/\/[^\/\s\)]+(?:\/[^\/\s\)]*)*?\/(?:#\/)?product\/([a-zA-Z0-9_-]+)/g,
        '/#/product/$1'
      );

      // Convert markdown links [text](url) to clickable links
      const parts = [];
      const regex = /\[([^\]]+)\]\(([^)]+)\)/g;
      let lastIndex = 0;
      let match;

      while ((match = regex.exec(processedContent)) !== null) {
        // Add text before the link
        if (match.index > lastIndex) {
          parts.push(
            <span key={`text-${lastIndex}`}>
              {processedContent.substring(lastIndex, match.index)}
            </span>
          );
        }

        // Add the link
        const linkText = match[1];
        let linkUrl = match[2];
        
        // Handle relative URLs - convert to full URL using current domain
        let finalUrl = linkUrl;
        if (linkUrl.startsWith('/#/')) {
          // Relative hash URL - use current origin
          finalUrl = window.location.origin + linkUrl;
        } else if (linkUrl.startsWith('/product/')) {
          // Convert to hash router format
          finalUrl = window.location.origin + '/#' + linkUrl;
        }
        
        const isProductLink = linkUrl.includes('/product/');
        
        parts.push(
          <a
            key={`link-${match.index}`}
            href={finalUrl}
            target="_self"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 underline font-semibold cursor-pointer"
            onClick={(e) => {
              if (isProductLink) {
                e.preventDefault();
                // Extract product ID and navigate using hash
                const productMatch = linkUrl.match(/\/(?:#\/)?product\/([a-zA-Z0-9_-]+)/);
                if (productMatch) {
                  window.location.hash = `/product/${productMatch[1]}`;
                }
              }
            }}
          >
            {linkText}
          </a>
        );

        lastIndex = regex.lastIndex;
      }

      // Add remaining text
      if (lastIndex < processedContent.length) {
        parts.push(
          <span key={`text-${lastIndex}`}>
            {processedContent.substring(lastIndex)}
          </span>
        );
      }

      return parts.length > 0 ? parts : content;
    } catch (error) {
      console.error('Error rendering message content:', error);
      return content;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleClearChat = () => {
    if (window.confirm('Clear all chat messages?')) {
      const initialMessage = {
        role: 'assistant',
        content: 'Hi! 👋 I\'m your AI Shopping Assistant. How can I help you find the perfect appliance today?',
        timestamp: new Date()
      };
      setMessages([initialMessage]);
      localStorage.removeItem('ai_chat_messages');
      localStorage.removeItem('ai_chat_session');
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      // Generate session ID if not exists
      const sessionId = sessionStorage.getItem('ai_chat_session') || `session_${Date.now()}`;
      sessionStorage.setItem('ai_chat_session', sessionId);

      // Call AI Sales Agent API
      const response = await fetch(`${BACKEND_URL}/api/ai/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_type: 'sales',
          message: inputMessage,
          session_id: sessionId,
          context: {}
        })
      });

      if (!response.ok) throw new Error('AI response failed');

      const data = await response.json();
      
      const assistantMessage = {
        role: 'assistant',
        content: data.response || 'I\'m here to help! Could you please rephrase that?',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I\'m having trouble connecting. Please try again or contact support.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    // Ensure text is properly handled on all devices
    const value = e.target.value;
    // Normalize the text to prevent any encoding issues
    const normalizedValue = value.normalize('NFC');
    setInputMessage(normalizedValue);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className={`fixed ${isMobile ? 'bottom-5 right-5' : 'bottom-6 right-6'} z-50 ${isMobile ? 'w-14 h-14' : 'w-16 h-16'} bg-gradient-to-r from-blue-600 to-purple-600 rounded-full shadow-2xl hover:shadow-3xl transition-all duration-300 flex items-center justify-center group hover:scale-110 chat-widget-button-mobile`}
        aria-label="Open AI Chat"
      >
        <MessageCircle className={`${isMobile ? 'w-7 h-7' : 'w-8 h-8'} text-white group-hover:scale-110 transition-transform`} />
        <div className={`absolute -top-2 -right-2 ${isMobile ? 'w-5 h-5' : 'w-6 h-6'} bg-red-500 rounded-full flex items-center justify-center`}>
          <Bot className={`${isMobile ? 'w-3 h-3' : 'w-4 h-4'} text-white`} />
        </div>
      </button>
    );
  }

  return (
    <div className={`fixed ${isMinimized ? 'bottom-6 right-6' : isMobile ? 'inset-0' : 'bottom-6 right-6'} z-50 transition-all duration-300`}>
      <div className={`bg-white ${isMobile && isOpen && !isMinimized 
        ? 'w-full h-full chat-widget-mobile' 
        : 'rounded-2xl shadow-2xl w-96 h-[600px]'
      } ${isMinimized ? 'w-80 h-16' : ''} flex flex-col overflow-hidden`}>
        {/* Header */}
        <div className="bg-gradient-to-r from-amber-700 to-orange-600 text-white p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
              <Bot className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-bold">Ai.ditya</h3>
              <p className="text-xs text-blue-100">Your AI Shopping Assistant</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleClearChat}
              className="p-1 hover:bg-white/20 rounded transition-colors text-xs"
              title="Clear chat"
            >
              🗑️
            </button>
            {!isMobile && (
              <button
                onClick={() => setIsMinimized(!isMinimized)}
                className="p-1 hover:bg-white/20 rounded transition-colors"
              >
                <Minimize2 className="w-5 h-5" />
              </button>
            )}
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 hover:bg-white/20 rounded transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {!isMinimized && (
          <>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-[80%] ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white rounded-2xl rounded-br-none'
                      : 'bg-white text-gray-900 rounded-2xl rounded-bl-none shadow-md'
                  } px-4 py-3`}>
                    {msg.role === 'assistant' && (
                      <div className="flex items-center gap-2 mb-1">
                        <Bot className="w-4 h-4 text-blue-600" />
                        <span className="text-xs font-semibold text-blue-600">AI Assistant</span>
                      </div>
                    )}
                    <div className="text-sm whitespace-pre-wrap">{renderMessageContent(msg.content)}</div>
                    <p className={`text-xs mt-1 ${msg.role === 'user' ? 'text-blue-100' : 'text-gray-400'}`}>
                      {msg.timestamp && typeof msg.timestamp.toLocaleTimeString === 'function' 
                        ? msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                        : new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                      }
                    </p>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-white rounded-2xl rounded-bl-none shadow-md px-4 py-3">
                    <Loader className="w-5 h-5 text-blue-600 animate-spin" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Quick Actions */}
            <div className="px-4 py-2 bg-white border-t border-gray-200">
              <div className="flex gap-2 overflow-x-auto">
                {['Show dishwashers', 'Compare ovens', 'Best microwave?'].map((action, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      setInputMessage(action);
                      setTimeout(() => handleSendMessage(), 100);
                    }}
                    className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-xs whitespace-nowrap transition-colors"
                  >
                    {action}
                  </button>
                ))}
              </div>
            </div>

            {/* Input */}
            <div className="p-4 bg-white border-t border-gray-200">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={handleInputChange}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me anything..."
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                  style={{ 
                    fontSize: '16px', // Prevent zoom on iOS
                    direction: 'ltr',
                    textAlign: 'left',
                    unicodeBidi: 'normal'
                  }}
                  autoComplete="off"
                  autoCorrect="off"
                  autoCapitalize="sentences"
                  spellCheck="true"
                  disabled={loading}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || loading}
                  className="bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed min-w-[48px] flex items-center justify-center"
                >
                  {loading ? (
                    <Loader className="w-5 h-5 animate-spin" />
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default AIChatWidget;
