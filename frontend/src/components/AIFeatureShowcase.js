import React from 'react';
import { Bot, Zap, Brain, MessageCircle, Truck, Wrench, ShoppingCart } from 'lucide-react';

const AIFeatureShowcase = ({ onAIChat }) => {
  const aiFeatures = [
    {
      id: 1,
      agentType: 'sales',
      icon: ShoppingCart,
      title: "AI Sales Agent",
      description: "Get personalized product recommendations, price negotiations, and expert buying advice",
      features: ["Product Recommendations", "Price Negotiations", "Feature Comparisons", "Bundle Suggestions"],
      color: "from-green-500 to-emerald-600",
      accent: "text-green-400",
      bgColor: "bg-green-50"
    },
    {
      id: 2,
      agentType: 'service',
      icon: Wrench,
      title: "AI Service Agent", 
      description: "24/7 technical support, troubleshooting guides, and automated service request creation",
      features: ["Instant Troubleshooting", "Service Requests", "Technical Support", "Repair Scheduling"],
      color: "from-blue-500 to-cyan-600",
      accent: "text-blue-400",
      bgColor: "bg-blue-50"
    },
    {
      id: 3,
      agentType: 'delivery',
      icon: Truck,
      title: "AI Delivery Agent",
      description: "Intelligent delivery optimization, real-time tracking, and proactive customer updates",
      features: ["Delivery Optimization", "Real-time Tracking", "Customer Updates", "Route Planning"],
      color: "from-teal-500 to-cyan-600",
      accent: "text-teal-400",
      bgColor: "bg-teal-50"
    }
  ];

  // Function to open chat with specific agent
  const openAgentChat = (agentType) => {
    // Dispatch custom event to open chat with specific agent
    window.dispatchEvent(new CustomEvent('openAIChatWithAgent', { detail: { agentType } }));
  };

  return (
    <div className="bg-gradient-to-br from-gray-50 to-blue-50 py-16">
      <div className="max-w-7xl mx-auto px-4">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-full mb-6">
            <Bot className="w-6 h-6 animate-pulse" />
            <span className="font-semibold">AI-Powered Ecommerce</span>
            <Zap className="w-5 h-5 text-yellow-300" />
          </div>
          
          <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-6">
            Meet Your <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">Intelligent</span> Shopping Assistants
          </h2>
          
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            Our advanced AI agents work 24/7 to provide personalized recommendations, 
            instant support, and seamless shopping experience tailored just for you.
          </p>

          <button
            onClick={onAIChat}
            className="group bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 rounded-2xl font-semibold text-lg transition-all duration-300 transform hover:scale-105 hover:shadow-2xl flex items-center space-x-3 mx-auto"
          >
            <MessageCircle className="w-6 h-6 group-hover:animate-bounce" />
            <span>Start AI Chat Now</span>
            <Bot className="w-6 h-6 group-hover:rotate-12 transition-transform" />
          </button>
        </div>

        {/* AI Agents Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8 mb-12">
          {aiFeatures.map((feature, index) => {
            const IconComponent = feature.icon;
            return (
              <div
                key={feature.id}
                className={`group relative overflow-hidden ${feature.bgColor} border border-gray-200 rounded-3xl p-8 hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2 cursor-pointer`}
                onClick={() => openAgentChat(feature.agentType)}
                style={{
                  animationDelay: `${index * 0.1}s`
                }}
              >
                {/* Background Gradient */}
                <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${feature.color} opacity-10 rounded-full transform translate-x-16 -translate-y-16 group-hover:scale-150 transition-transform duration-500`} />
                
                {/* Icon */}
                <div className={`inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br ${feature.color} text-white rounded-2xl mb-6 group-hover:rotate-12 transition-transform duration-300`}>
                  <IconComponent className="w-8 h-8" />
                </div>

                {/* Content */}
                <h3 className="text-2xl font-bold text-gray-900 mb-4 group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-blue-600 group-hover:to-purple-600 transition-all duration-300">
                  {feature.title}
                </h3>
                
                <p className="text-gray-600 mb-6 leading-relaxed">
                  {feature.description}
                </p>

                {/* Features List */}
                <ul className="space-y-2">
                  {feature.features.map((item, idx) => (
                    <li key={idx} className="flex items-center space-x-3">
                      <div className={`w-2 h-2 ${feature.color} bg-gradient-to-r rounded-full`} />
                      <span className="text-sm text-gray-700 font-medium">{item}</span>
                    </li>
                  ))}
                </ul>

                {/* Hover Effect */}
                <div className="absolute inset-0 bg-gradient-to-br from-white/0 to-white/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-3xl" />
                
                {/* AI Badge */}
                <div className="absolute top-4 right-4 bg-white/80 backdrop-blur-sm rounded-full p-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <Bot className={`w-4 h-4 ${feature.accent} animate-pulse`} />
                </div>
              </div>
            );
          })}
        </div>

        {/* Stats Section */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {[
            { number: "24/7", label: "AI Support Available", icon: Bot },
            { number: "3", label: "Intelligent Agents", icon: Zap },
            { number: "99%", label: "Response Accuracy", icon: Brain },
            { number: "<1s", label: "Average Response Time", icon: MessageCircle }
          ].map((stat, index) => {
            const IconComponent = stat.icon;
            return (
              <div
                key={index}
                className="text-center p-6 bg-white rounded-2xl border border-gray-200 hover:shadow-lg transition-all duration-300 transform hover:scale-105"
              >
                <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 text-white rounded-xl mb-4">
                  <IconComponent className="w-6 h-6" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-2">{stat.number}</div>
                <div className="text-gray-600 font-medium">{stat.label}</div>
              </div>
            );
          })}
        </div>

        {/* Call to Action */}
        <div className="text-center bg-gradient-to-r from-blue-600 to-purple-600 rounded-3xl p-12 text-white">
          <h3 className="text-3xl font-bold mb-4">
            Experience the Future of Shopping Today
          </h3>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Join thousands of satisfied customers who trust our AI-powered platform for all their home appliance needs.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={onAIChat}
              className="bg-white text-blue-600 px-8 py-4 rounded-2xl font-semibold text-lg hover:bg-gray-100 transition-colors flex items-center justify-center space-x-2"
            >
              <Bot className="w-6 h-6" />
              <span>Chat with AI Now</span>
            </button>
            <button className="bg-transparent border-2 border-white text-white px-8 py-4 rounded-2xl font-semibold text-lg hover:bg-white hover:text-blue-600 transition-colors">
              Learn More
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIFeatureShowcase;