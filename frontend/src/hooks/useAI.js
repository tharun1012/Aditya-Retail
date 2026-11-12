import { useState, useEffect, useCallback } from 'react';
import { aiAPI } from '../services/api';

export const useAIChat = (agentType = 'sales') => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);

  // Load chat history on mount or agent change
  useEffect(() => {
    const loadChatHistory = async () => {
      try {
        const response = await aiAPI.getChatHistory(agentType);
        setChatHistory(response.messages || []);
        
        // Convert backend messages to frontend format
        const formattedMessages = response.messages.map(msg => ({
          id: msg.id,
          sender: msg.sender,
          agent: msg.agent_type,
          text: msg.message,
          timestamp: new Date(msg.timestamp),
          context: msg.context
        }));
        
        setMessages(formattedMessages);
      } catch (err) {
        console.error('Failed to load chat history:', err);
        setError(err.message);
      }
    };

    loadChatHistory();
  }, [agentType]);

  const sendMessage = useCallback(async (message, context = {}) => {
    if (!message.trim()) return;

    setLoading(true);
    setError(null);

    // Add user message immediately for better UX
    const userMessage = {
      id: Date.now().toString(),
      sender: 'user',
      agent: agentType,
      text: message,
      timestamp: new Date(),
      context
    };
    
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await aiAPI.chat(agentType, message, context);
      
      // Add AI response
      const aiMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        agent: agentType,
        text: response.response,
        timestamp: new Date(response.timestamp),
        context: { agent_type: agentType }
      };
      
      setMessages(prev => [...prev, aiMessage]);
      return response;
      
    } catch (err) {
      setError(err.message || 'Failed to send message');
      
      // Add error message to chat
      const errorMessage = {
        id: (Date.now() + 2).toString(),
        sender: 'ai',
        agent: agentType,
        text: 'I apologize, but I\'m experiencing technical difficulties. Please try again.',
        timestamp: new Date(),
        context: { error: true }
      };
      
      setMessages(prev => [...prev, errorMessage]);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [agentType]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  const switchAgent = useCallback((newAgentType) => {
    // This will trigger the useEffect to load new agent's history
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    loading,
    error,
    sendMessage,
    clearMessages,
    switchAgent,
    chatHistory
  };
};

export const useServiceRequest = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const createServiceRequest = useCallback(async (serviceData) => {
    setLoading(true);
    setError(null);

    try {
      const response = await aiAPI.createServiceRequest(serviceData);
      return response;
    } catch (err) {
      setError(err.message || 'Failed to create service request');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    createServiceRequest,
    loading,
    error
  };
};

export const useInventoryInsights = () => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchAnalysis = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await aiAPI.getInventoryAnalysis();
      setAnalysis(response);
      return response;
    } catch (err) {
      setError(err.message || 'Failed to fetch inventory analysis');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAnalysis();
  }, [fetchAnalysis]);

  return {
    analysis,
    loading,
    error,
    refresh: fetchAnalysis
  };
};

export const useMarketingInsights = () => {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchInsights = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await aiAPI.getMarketingInsights();
      setInsights(response);
      return response;
    } catch (err) {
      setError(err.message || 'Failed to fetch marketing insights');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInsights();
  }, [fetchInsights]);

  return {
    insights,
    loading,
    error,
    refresh: fetchInsights
  };
};

export const useDashboardSummary = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchSummary = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await aiAPI.getDashboardSummary();
      setSummary(response);
      return response;
    } catch (err) {
      setError(err.message || 'Failed to fetch dashboard summary');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSummary();
  }, [fetchSummary]);

  return {
    summary,
    loading,
    error,
    refresh: fetchSummary
  };
};