import React, { useState, useEffect, useRef } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  Bot, Send, X, ShoppingBag, Wrench, Truck, Sparkles, 
  User, Phone, Mail, ExternalLink, Loader, CheckCircle,
  AlertCircle, Package, MapPin, ShoppingCart, History, MessageCircle
} from 'lucide-react';
import { useCart } from '../hooks/useCart';
import { useAuth } from '../contexts/AuthContext';


const NeuralAIChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [collectedData, setCollectedData] = useState({});
  const [addingToCart, setAddingToCart] = useState(null);
  const [showPreviousSessions, setShowPreviousSessions] = useState(false);
  const [previousSessions, setPreviousSessions] = useState([]);
  const [loadingSessions, setLoadingSessions] = useState(false);
  const messagesEndRef = useRef(null);
  
  // Use cart from context
  const { addToCart } = useCart();
  
  // Use auth context for user context retention
  const { user, isAuthenticated } = useAuth();

  // Agent configurations
  const agents = [
    {
      type: 'sales',
      name: 'Sales Agent',
      icon: ShoppingBag,
      color: 'blue',
      gradient: 'from-blue-500 to-indigo-600',
      description: 'Product recommendations & purchase assistance',
      welcome: "👋 Hi! I'm your Sales Agent. I can help you find the perfect products for your needs. What are you looking for today?"
    },
    {
      type: 'service',
      name: 'Service Agent',
      icon: Wrench,
      color: 'orange',
      gradient: 'from-orange-500 to-red-600',
      description: 'Technical support & troubleshooting',
      welcome: "🔧 Hello! I'm your Service Agent. I can help diagnose issues and create service tickets if needed. What product are you having trouble with?"
    },
    {
      type: 'delivery',
      name: 'Delivery Agent',
      icon: Truck,
      color: 'green',
      gradient: 'from-green-500 to-teal-600',
      description: 'Order tracking & delivery updates',
      welcome: "🚚 Hi! I'm your Delivery Agent. I can help track your orders and resolve delivery issues. What's your order number?"
    }
  ];

  // Load previous session from localStorage or check for user sessions
  useEffect(() => {
    // Try to restore last session from localStorage
    const savedSessionId = localStorage.getItem('ai_chat_session_id');
    const savedAgent = localStorage.getItem('ai_chat_agent');
    
    if (savedSessionId && savedAgent) {
      setSessionId(savedSessionId);
      // Don't auto-select agent - let user choose or resume
    }
  }, []);

  // Listen for event to open chat with specific agent
  useEffect(() => {
    const handleOpenWithAgent = (event) => {
      const { agentType } = event.detail || {};
      if (agentType) {
        // Generate new session for direct agent access
        const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        setSessionId(newSessionId);
        localStorage.setItem('ai_chat_session_id', newSessionId);
        
        // Select the agent and open chat
        const agent = agents.find(a => a.type === agentType);
        if (agent) {
          setSelectedAgent(agentType);
          localStorage.setItem('ai_chat_agent', agentType);
          setMessages([{
            type: 'ai',
            content: agent.welcome,
            timestamp: new Date(),
            agent: agentType
          }]);
        }
        setIsOpen(true);
      }
    };

    window.addEventListener('openAIChatWithAgent', handleOpenWithAgent);
    return () => window.removeEventListener('openAIChatWithAgent', handleOpenWithAgent);
  }, [agents]);

  // Listen for generic openAIChat event (from product pages)
  useEffect(() => {
    const handleOpenAIChat = (event) => {
      const { product } = event.detail || {};
      
      // Generate new session
      const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      setSessionId(newSessionId);
      localStorage.setItem('ai_chat_session_id', newSessionId);
      
      // Open with sales agent
      const salesAgent = agents.find(a => a.type === 'sales');
      if (salesAgent) {
        setSelectedAgent('sales');
        localStorage.setItem('ai_chat_agent', 'sales');
        
        // If product context provided, create a product inquiry message
        if (product) {
          setMessages([
            {
              type: 'ai',
              content: salesAgent.welcome,
              timestamp: new Date(),
              agent: 'sales'
            },
            {
              type: 'user',
              content: `I'm interested in the ${product.name || 'this product'}. Can you tell me more about it?`,
              timestamp: new Date()
            }
          ]);
          // Auto-send inquiry about the product
          setTimeout(() => {
            handleSendWithProduct(product);
          }, 500);
        } else {
          setMessages([{
            type: 'ai',
            content: salesAgent.welcome,
            timestamp: new Date(),
            agent: 'sales'
          }]);
        }
      }
      setIsOpen(true);
    };
    
    const handleSendWithProduct = async (product) => {
      if (!product) return;
      
      const productContext = {
        product_id: product.id,
        product_name: product.name,
        price: product.price,
        brand: product.brand,
        category: product.category
      };
      
      try {
        const currentSessionId = localStorage.getItem('ai_chat_session_id');
        const response = await fetch(`${BACKEND_URL}/api/neural-ai/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: currentSessionId,
            agent_type: 'sales',
            message: `I'm interested in the ${product.name}. Can you tell me more about it and help me with the best price?`,
            context: productContext
          })
        });
        
        const data = await response.json();
        if (data.status === 'success') {
          setMessages(prev => [...prev, {
            type: 'ai',
            content: data.response,
            timestamp: new Date(),
            agent: 'sales'
          }]);
        }
      } catch (error) {
        console.error('Error sending product inquiry:', error);
      }
    };

    window.addEventListener('openAIChat', handleOpenAIChat);
    return () => window.removeEventListener('openAIChat', handleOpenAIChat);
  }, [agents]);

  useEffect(() => {
    if (isOpen && !sessionId) {
      // Generate session ID when widget opens
      const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      setSessionId(newSessionId);
      localStorage.setItem('ai_chat_session_id', newSessionId);
    }
  }, [isOpen, sessionId]);

  // Fetch previous sessions for logged-in users
  useEffect(() => {
    if (isAuthenticated && user?.id && isOpen && !selectedAgent) {
      fetchPreviousSessions();
    }
  }, [isAuthenticated, user, isOpen, selectedAgent]);

  const fetchPreviousSessions = async () => {
    if (!user?.id) return;
    
    setLoadingSessions(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/neural-ai/user-sessions/${user.id}?limit=5`);
      const data = await response.json();
      
      if (data.status === 'success' && data.sessions?.length > 0) {
        setPreviousSessions(data.sessions);
      }
    } catch (error) {
      console.error('Error fetching previous sessions:', error);
    } finally {
      setLoadingSessions(false);
    }
  };

  const resumePreviousSession = async (session) => {
    setIsLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/neural-ai/resume-session?session_id=${session.session_id}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setSessionId(session.session_id);
        setSelectedAgent(session.agent_type);
        setCollectedData(data.collected_data || {});
        
        // Convert stored messages to display format
        const restoredMessages = data.messages.map(msg => ({
          type: msg.sender === 'user' ? 'user' : 'ai',
          content: msg.sender === 'user' ? msg.message : formatAIResponse(msg.message),
          rawContent: msg.message,
          timestamp: new Date(msg.timestamp),
          agent: msg.agent_type
        }));
        
        setMessages(restoredMessages);
        localStorage.setItem('ai_chat_session_id', session.session_id);
        localStorage.setItem('ai_chat_agent', session.agent_type);
        setShowPreviousSessions(false);
      }
    } catch (error) {
      console.error('Error resuming session:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const selectAgent = (agentType) => {
    const agent = agents.find(a => a.type === agentType);
    setSelectedAgent(agentType);
    localStorage.setItem('ai_chat_agent', agentType);
    
    // Add welcome message
    setMessages([{
      type: 'ai',
      content: agent.welcome,
      timestamp: new Date(),
      agent: agentType
    }]);
  };

  const sendMessage = async () => {
    const textToSend = inputMessage.trim();
    
    if (!textToSend || !selectedAgent) return;

    // Add user message
    const userMessage = {
      type: 'user',
      content: textToSend,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`${BACKEND_URL}/api/neural-ai/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_type: selectedAgent,
          message: textToSend,
          session_id: sessionId,
          user_id: user?.id || null,  // Include user_id for context retention
          context: {
            collected_data: collectedData,
            user_name: user?.first_name || user?.email?.split('@')[0] || null,
            user_email: user?.email || null
          }
        })
      });

      const data = await response.json();

      if (data.status === 'success') {
        // Parse and format AI response
        const formattedContent = formatAIResponse(data.response);
        
        // Add AI response
        const aiMessage = {
          type: 'ai',
          content: formattedContent,
          rawContent: data.response,
          timestamp: new Date(),
          agent: selectedAgent,
          collectedData: data.collected_data,
          actionRequired: data.action_required,
          confidence: data.confidence
        };

        setMessages(prev => [...prev, aiMessage]);
        
        // Update collected data
        if (data.collected_data) {
          setCollectedData(prev => ({ ...prev, ...data.collected_data }));
        }

        // Handle special actions
        handleActionRequired(data.action_required, data);
      }
    } catch (error) {
      console.error('Neural AI error:', error);
      
      const errorMessage = {
        type: 'ai',
        content: "I apologize for the inconvenience. I'm experiencing technical difficulties. Please try again in a moment.",
        timestamp: new Date(),
        agent: selectedAgent,
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatAIResponse = (response) => {
    // Convert product links format: [Product Name](PRODUCT_LINK:id) to clickable links
    let formatted = response;
    
    // Product links with Add to Cart button
    formatted = formatted.replace(
      /\[([^\]]+)\]\(PRODUCT_LINK:([^)]+)\)/g,
      '<span class="inline-flex items-center gap-2"><a href="/#/product/$2" target="_blank" class="text-blue-600 hover:text-blue-800 underline font-semibold">$1 🔗</a><button data-product-id="$2" class="add-to-cart-btn bg-green-500 hover:bg-green-600 text-white text-xs px-2 py-1 rounded flex items-center gap-1 transition-colors"><svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>Add</button></span>'
    );
    
    // Manual links
    formatted = formatted.replace(
      /\[([^\]]+)\]\(MANUAL_LINK:([^)]+)\)/g,
      '<a href="$2" target="_blank" class="text-purple-600 hover:text-purple-800 underline">$1 📄</a>'
    );
    
    // Tech specs links
    formatted = formatted.replace(
      /\[([^\]]+)\]\(SPECS_LINK:([^)]+)\)/g,
      '<a href="$2" target="_blank" class="text-indigo-600 hover:text-indigo-800 underline">$1 📋</a>'
    );
    
    // Tracking links
    formatted = formatted.replace(
      /\[([^\]]+)\]\(TRACKING_LINK:([^)]+)\)/g,
      '<a href="$2" target="_blank" class="text-green-600 hover:text-green-800 underline">$1 📦</a>'
    );
    
    return formatted;
  };

  const handleActionRequired = (action, data) => {
    switch (action) {
      case 'ticket_created':
        // Show success notification
        showNotification('Service ticket created successfully!', 'success');
        break;
      case 'showing_products':
        // Products are being shown, maybe highlight them
        break;
      case 'ready_to_close':
        // Lead data collected, show summary
        if (data.collected_data) {
          showCollectedDataSummary(data.collected_data);
        }
        break;
      case 'add_to_cart':
        // Handle add to cart request from AI
        if (data.product_id) {
          handleAddToCart(data.product_id);
        }
        break;
      default:
        break;
    }
  };

  // Add product to cart
  const handleAddToCart = async (productId) => {
    setAddingToCart(productId);
    try {
      const success = await addToCart(productId, 1);
      if (success) {
        // Add confirmation message
        const confirmMessage = {
          type: 'system',
          content: `✅ Product added to cart successfully! You can continue browsing or proceed to checkout.`,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, confirmMessage]);
        showNotification('Product added to cart!', 'success');
      } else {
        throw new Error('Failed to add to cart');
      }
    } catch (error) {
      console.error('Add to cart error:', error);
      const errorMessage = {
        type: 'system',
        content: `❌ Sorry, couldn't add the product to cart. Please try again.`,
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setAddingToCart(null);
    }
  };

  const showNotification = (message, type = 'info') => {
    // Simple notification - can be enhanced with toast library
    console.log(`${type.toUpperCase()}: ${message}`);
  };

  const showCollectedDataSummary = (data) => {
    // Add a special message showing collected data
    const summaryMessage = {
      type: 'system',
      content: '📋 Lead Information Captured',
      data: data,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, summaryMessage]);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const resetChat = () => {
    setSelectedAgent(null);
    setMessages([]);
    setCollectedData({});
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);
    localStorage.setItem('ai_chat_session_id', newSessionId);
    localStorage.removeItem('ai_chat_agent');
    setShowPreviousSessions(false);
    // Refresh previous sessions if user is logged in
    if (isAuthenticated && user?.id) {
      fetchPreviousSessions();
    }
  };

  const currentAgent = agents.find(a => a.type === selectedAgent);

  // WhatsApp number
  const whatsappNumber = '919844577440';
  const whatsappUrl = `https://wa.me/${whatsappNumber}`;

  return (
    <>
      {/* Floating Buttons Container */}
{!isOpen && (
  <div className="fixed bottom-24 right-4 z-[9997]">

    {/* AI Chat Button */}
    <button
      onClick={() => setIsOpen(true)}
      className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white p-4 rounded-full shadow-2xl hover:shadow-3xl transform hover:scale-110 transition-all duration-300 animate-pulse flex items-center justify-center"
      style={{ width: '52px', height: '52px' }}
      title="AI Assistant"
      data-testid="ai-chat-widget-btn"
    >
      <Sparkles className="h-5 w-5" />
    </button>
  </div>
)}

      {/* Chat Window */}
      {isOpen && (
        <>
          {/* WhatsApp Button - visible when chat is open */}
          <a
            href={whatsappUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="fixed bottom-6 right-[520px] bg-green-500 hover:bg-green-600 text-white p-4 rounded-full shadow-2xl hover:shadow-3xl transform hover:scale-110 transition-all duration-300 z-50 flex items-center justify-center"
            title="Chat on WhatsApp"
            data-testid="whatsapp-chat-btn-open"
          >
            <svg 
              viewBox="0 0 24 24" 
              className="h-6 w-6 fill-current"
            >
              <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
            </svg>
          </a>
          
          <div className="fixed bottom-6 right-6 w-[480px] h-[700px] bg-white rounded-2xl shadow-2xl flex flex-col z-50 border border-gray-200">
          {/* Header */}
          <div className={`bg-gradient-to-r ${currentAgent ? currentAgent.gradient : 'from-purple-600 to-indigo-600'} text-white p-4 rounded-t-2xl flex items-center justify-between`}>
            <div className="flex items-center space-x-3">
              {currentAgent ? (
                <>
                  <currentAgent.icon className="h-6 w-6" />
                  <div>
                    <h3 className="font-bold text-lg">{currentAgent.name}</h3>
                    <p className="text-xs text-white/80">{currentAgent.description}</p>
                  </div>
                </>
              ) : (
                <>
                  <Sparkles className="h-5 w-5" />
                  <div>
                    <h3 className="font-bold text-lg">AI Assistant</h3>
                    <p className="text-xs text-white/80">Choose how I can help you</p>
                  </div>
                </>
              )}
            </div>
            <div className="flex items-center space-x-2">
              {selectedAgent && (
                <button
                  onClick={resetChat}
                  className="p-2 hover:bg-white/20 rounded-lg transition-colors"
                  title="Change Agent"
                >
                  <Bot className="h-5 w-5" />
                </button>
              )}
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Agent Selection or Chat */}
          {!selectedAgent ? (
            <div className="flex-1 p-6 overflow-y-auto">
              <div className="text-center mb-6">
                <div className="inline-block p-4 bg-gradient-to-r from-purple-100 to-indigo-100 rounded-full mb-4">
                  <Sparkles className="h-12 w-12 text-purple-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  Welcome to Aditya Retail AI
                </h2>
                <p className="text-gray-600">
                  Powered by Neural AI • Choose an assistant to get started
                </p>
              </div>

              {/* Previous Sessions for logged-in users */}
              {isAuthenticated && previousSessions.length > 0 && (
                <div className="mb-6">
                  <button
                    onClick={() => setShowPreviousSessions(!showPreviousSessions)}
                    className="w-full flex items-center justify-between p-3 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                    data-testid="show-previous-sessions"
                  >
                    <div className="flex items-center gap-2">
                      <History className="w-5 h-5 text-gray-600" />
                      <span className="font-medium text-gray-700">Continue Previous Conversation</span>
                    </div>
                    <span className="text-sm text-gray-500">{previousSessions.length} sessions</span>
                  </button>
                  
                  {showPreviousSessions && (
                    <div className="mt-2 space-y-2" data-testid="previous-sessions-list">
                      {previousSessions.map((session, idx) => {
                        const agentInfo = agents.find(a => a.type === session.agent_type);
                        const AgentIcon = agentInfo?.icon || MessageCircle;
                        return (
                          <button
                            key={idx}
                            onClick={() => resumePreviousSession(session)}
                            className="w-full p-3 bg-white border border-gray-200 rounded-lg hover:border-purple-300 hover:bg-purple-50 transition-all text-left"
                            disabled={isLoading}
                          >
                            <div className="flex items-start gap-3">
                              <div className={`p-2 rounded-lg bg-gradient-to-r ${agentInfo?.gradient || 'from-gray-400 to-gray-500'}`}>
                                <AgentIcon className="w-4 h-4 text-white" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2">
                                  <span className="font-medium text-gray-800 text-sm">
                                    {agentInfo?.name || session.agent_type}
                                  </span>
                                  <span className="text-xs text-gray-400">
                                    {session.message_count} messages
                                  </span>
                                </div>
                                <p className="text-xs text-gray-500 truncate mt-1">
                                  {session.last_message}
                                </p>
                                <p className="text-xs text-gray-400 mt-1">
                                  {new Date(session.last_timestamp).toLocaleDateString('en-IN', {
                                    day: 'numeric',
                                    month: 'short',
                                    hour: '2-digit',
                                    minute: '2-digit'
                                  })}
                                </p>
                              </div>
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}

              <div className="space-y-4">
                {agents.map((agent) => {
                  const Icon = agent.icon;
                  return (
                    <button
                      key={agent.type}
                      onClick={() => selectAgent(agent.type)}
                      className={`w-full p-6 bg-gradient-to-r ${agent.gradient} text-white rounded-xl hover:shadow-lg transform hover:scale-105 transition-all duration-300 text-left`}
                      data-testid={`select-agent-${agent.type}`}
                    >
                      <div className="flex items-start space-x-4">
                        <div className="p-3 bg-white/20 rounded-lg">
                          <Icon className="h-8 w-8" />
                        </div>
                        <div className="flex-1">
                          <h3 className="font-bold text-lg mb-1">{agent.name}</h3>
                          <p className="text-sm text-white/90">{agent.description}</p>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>

              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-start space-x-3">
                  <Sparkles className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm text-blue-900 font-semibold mb-1">
                      Powered by Gemini 2.5 Pro
                    </p>
                    <p className="text-xs text-blue-700">
                      Advanced AI with deep product knowledge, multi-language support, and human-like conversations
                      {isAuthenticated && <span className="block mt-1 text-purple-600 font-medium">✓ Context retention enabled for your account</span>}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <>
              {/* Chat Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    {message.type === 'system' ? (
                      <div className="bg-green-50 border border-green-200 rounded-lg p-4 max-w-[85%]">
                        <div className="flex items-center space-x-2 mb-2">
                          <CheckCircle className="h-5 w-5 text-green-600" />
                          <p className="font-semibold text-green-900">{message.content}</p>
                        </div>
                        {message.data && (
                          <div className="mt-2 space-y-1 text-sm">
                            {message.data.name && (
                              <div className="flex items-center space-x-2">
                                <User className="h-4 w-4 text-gray-600" />
                                <span className="text-gray-700">{message.data.name}</span>
                              </div>
                            )}
                            {message.data.phone && (
                              <div className="flex items-center space-x-2">
                                <Phone className="h-4 w-4 text-gray-600" />
                                <span className="text-gray-700">{message.data.phone}</span>
                              </div>
                            )}
                            {message.data.email && (
                              <div className="flex items-center space-x-2">
                                <Mail className="h-4 w-4 text-gray-600" />
                                <span className="text-gray-700">{message.data.email}</span>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    ) : message.type === 'user' ? (
                      <div className="bg-blue-600 text-white rounded-2xl rounded-tr-sm px-4 py-3 max-w-[75%] shadow-md">
                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      </div>
                    ) : (
                      <div className={`${message.isError ? 'bg-red-50 border border-red-200' : 'bg-white border border-gray-200'} rounded-2xl rounded-tl-sm px-4 py-3 max-w-[85%] shadow-md`}>
                        <div
                          className="text-sm text-gray-800 whitespace-pre-wrap"
                          dangerouslySetInnerHTML={{ __html: message.content }}
                          onClick={(e) => {
                            // Handle Add to Cart button clicks
                            if (e.target.classList.contains('add-to-cart-btn') || e.target.closest('.add-to-cart-btn')) {
                              const btn = e.target.classList.contains('add-to-cart-btn') ? e.target : e.target.closest('.add-to-cart-btn');
                              const productId = btn.getAttribute('data-product-id');
                              if (productId && !addingToCart) {
                                handleAddToCart(productId);
                              }
                            }
                          }}
                        />
                        <p className="text-xs text-gray-400 mt-2">
                          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </p>
                      </div>
                    )}
                  </div>
                ))}
                
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3 shadow-md">
                      <div className="flex items-center space-x-2">
                        <Loader className="h-4 w-4 animate-spin text-blue-600" />
                        <span className="text-sm text-gray-600">Thinking...</span>
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="p-4 border-t border-gray-200 bg-white rounded-b-2xl">
                <div className="flex items-end space-x-2">
                  <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message..."
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-xl resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows="2"
                    disabled={isLoading}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={isLoading || !inputMessage.trim()}
                    className={`p-3 rounded-xl transition-colors ${
                      isLoading || !inputMessage.trim()
                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        : `bg-gradient-to-r ${currentAgent.gradient} text-white hover:shadow-lg transform hover:scale-105`
                    }`}
                  >
                    <Send className="h-5 w-5" />
                  </button>
                </div>
                
                <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
                  <span>Powered by Neural AI (Gemini 2.5 Pro)</span>
                  {collectedData && Object.keys(collectedData).length > 0 && (
                    <span className="text-green-600 font-semibold">
                      ✓ {Object.keys(collectedData).length} details collected
                    </span>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
        </>
      )}
    </>
  );
};

export default NeuralAIChatWidget;
