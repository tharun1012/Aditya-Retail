import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Bot, User, Zap, Wrench, Package, TrendingUp, Truck } from 'lucide-react';
import { useAIChat } from '../hooks/useAI';

const AIChat = ({ isOpen, onClose, selectedProduct }) => {
  const [activeAgent, setActiveAgent] = useState('sales');
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef(null);
  
  // Use real AI chat hook
  const { messages, loading: isTyping, error, sendMessage, switchAgent } = useAIChat(activeAgent);

  const agents = [
    { id: 'sales', name: 'Ai.ditya', icon: Zap, color: 'bg-amber-600', description: 'Your AI Shopping Assistant' },
    { id: 'service', name: 'Service Agent', icon: Wrench, color: 'bg-blue-500', description: 'Support & troubleshooting' },
    { id: 'delivery', name: 'Delivery Agent', icon: Truck, color: 'bg-teal-500', description: 'Order tracking & delivery' }
  ];

  useEffect(() => {
    if (selectedProduct && activeAgent === 'sales' && isOpen) {
      // Send product-specific message when product is selected
      const productContext = {
        product: {
          id: selectedProduct.id,
          name: selectedProduct.name,
          price: selectedProduct.price,
          brand: selectedProduct.brand,
          category: selectedProduct.category,
          stock: selectedProduct.stock
        }
      };
      
      const productMessage = `I'm interested in the ${selectedProduct.name}. Can you tell me more about it and help me with the best price?`;
      sendMessage(productMessage, productContext);
    }
  }, [selectedProduct, activeAgent, isOpen]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;
    
    try {
      await sendMessage(inputMessage);
      setInputMessage('');
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleSwitchAgent = (agentId) => {
    setActiveAgent(agentId);
    switchAgent(agentId);
  };

  const currentAgent = agents.find(agent => agent.id === activeAgent);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-t-xl">
          <div className="flex items-center space-x-3">
            <MessageCircle className="w-6 h-6" />
            <div>
              <h2 className="text-xl font-bold">AI Assistant Hub</h2>
              <p className="text-sm opacity-90">Your 24/7 intelligent support team</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/20 rounded-lg transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="flex flex-1 overflow-hidden">
          {/* Agent Selection Sidebar */}
          <div className="w-80 bg-gray-50 border-r flex flex-col">
            <div className="p-4">
              <h3 className="font-semibold text-gray-800 mb-3">Select AI Agent</h3>
              <div className="space-y-2">
                {agents.map((agent) => {
                  const IconComponent = agent.icon;
                  return (
                    <button
                      key={agent.id}
                      onClick={() => handleSwitchAgent(agent.id)}
                      className={`w-full p-3 rounded-lg text-left transition-all ${
                        activeAgent === agent.id
                          ? 'bg-white shadow-md border-2 border-blue-200'
                          : 'hover:bg-white hover:shadow-sm'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <div className={`p-2 rounded-lg ${agent.color} text-white`}>
                          <IconComponent className="w-5 h-5" />
                        </div>
                        <div className="flex-1">
                          <div className="font-medium text-gray-800">{agent.name}</div>
                          <div className="text-xs text-gray-600">{agent.description}</div>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Current Agent Info */}
            <div className="mt-auto p-4 bg-white border-t">
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-lg ${currentAgent.color} text-white`}>
                  <currentAgent.icon className="w-5 h-5" />
                </div>
                <div>
                  <div className="font-medium text-gray-800">Active: {currentAgent.name}</div>
                  <div className="text-xs text-green-600">● Online</div>
                </div>
              </div>
            </div>
          </div>

          {/* Chat Area */}
          <div className="flex-1 flex flex-col">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`flex items-start space-x-2 max-w-[80%] ${
                    message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                  }`}>
                    <div className={`p-2 rounded-full ${
                      message.sender === 'user' 
                        ? 'bg-blue-100' 
                        : currentAgent.color
                    }`}>
                      {message.sender === 'user' ? (
                        <User className="w-4 h-4 text-blue-700" />
                      ) : (
                        <Bot className="w-4 h-4 text-white" />
                      )}
                    </div>
                    <div className={`rounded-lg p-3 ${
                      message.sender === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      <div className="whitespace-pre-wrap">{message.text}</div>
                      <div className={`text-xs mt-1 ${
                        message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}>
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              
              {/* Typing Indicator */}
              {isTyping && (
                <div className="flex justify-start">
                  <div className="flex items-start space-x-2">
                    <div className={`p-2 rounded-full ${currentAgent.color}`}>
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                    <div className="bg-gray-100 rounded-lg p-3">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t p-4 bg-gray-50">
              <div className="flex space-x-3">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder={`Ask ${currentAgent.name} anything...`}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim()}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIChat;