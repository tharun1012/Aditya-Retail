import React from 'react';
import { Bot, MessageCircle, Truck, Wrench, Sparkles, ArrowRight, Zap } from 'lucide-react';

const PremiumAIShowcase = ({ onAgentClick }) => {
  const agents = [
    {
      id: 'sales',
      icon: MessageCircle,
      title: 'AI Sales Consultant',
      description: 'Expert recommendations tailored to your lifestyle and budget.',
      features: ['Personalized Suggestions', 'Price Negotiations', 'Comparison Analysis'],
      gradient: 'from-emerald-500 to-teal-600',
      glow: 'shadow-emerald-500/20'
    },
    {
      id: 'service',
      icon: Wrench,
      title: 'AI Service Expert',
      description: 'Instant troubleshooting, warranty assistance, and scheduling.',
      features: ['24/7 Support', 'Video Diagnostics', 'Service Booking'],
      gradient: 'from-blue-500 to-indigo-600',
      glow: 'shadow-blue-500/20'
    },
    {
      id: 'delivery',
      icon: Truck,
      title: 'AI Delivery Tracker',
      description: 'Real-time updates on your order from warehouse to doorstep.',
      features: ['Live Tracking', 'Slot Selection', 'Installation Help'],
      gradient: 'from-violet-500 to-purple-600',
      glow: 'shadow-violet-500/20'
    }
  ];

  const handleAgentClick = (agentId) => {
    window.dispatchEvent(new CustomEvent('openAIChatWithAgent', { detail: { agentType: agentId } }));
  };

  return (
    <section className="relative py-12 sm:py-16 md:py-24 lg:py-32 bg-cream overflow-hidden">
      {/* Background Pattern - Subtle on mobile */}
      <div className="absolute inset-0 opacity-20 md:opacity-30">
        <div className="absolute top-0 left-1/4 w-48 sm:w-64 md:w-96 h-48 sm:h-64 md:h-96 bg-gradient-to-br from-blue-200 to-purple-200 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-48 sm:w-64 md:w-96 h-48 sm:h-64 md:h-96 bg-gradient-to-br from-emerald-200 to-teal-200 rounded-full blur-3xl" />
      </div>

      <div className="relative max-w-[1400px] mx-auto px-4 sm:px-6 md:px-12">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-8 sm:mb-12 md:mb-16">
          <div className="inline-flex items-center gap-2 bg-obsidian/5 border border-obsidian/10 px-3 py-1.5 md:px-4 md:py-2 rounded-full mb-4 md:mb-6">
            <Zap className="w-3 h-3 md:w-4 md:h-4 text-copper" />
            <span className="font-body text-xs md:text-sm text-obsidian/70">Powered by Advanced AI</span>
          </div>
          
          <h2 className="font-display text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl text-obsidian mb-3 md:mb-6 tracking-tight">
            Your Personal
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600"> AI Team</span>
          </h2>
          
          <p className="font-body text-sm sm:text-base md:text-lg text-obsidian/60 leading-relaxed px-4 sm:px-0">
            Three specialized AI assistants working together for an exceptional shopping experience. Available 24/7.
          </p>
        </div>

        {/* AI Agents Grid - Single column until lg screens */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6 lg:gap-8">
          {agents.map((agent, index) => {
            const IconComponent = agent.icon;
            return (
              <div
                key={agent.id}
                onClick={() => handleAgentClick(agent.id)}
                className={`group relative bg-white rounded-2xl lg:rounded-3xl p-5 md:p-6 lg:p-8 border border-platinum hover:border-transparent cursor-pointer transition-all duration-500 ease-premium hover:-translate-y-1 lg:hover:-translate-y-2 hover:shadow-xl lg:hover:shadow-2xl ${agent.glow}`}
                style={{ animationDelay: `${index * 100}ms` }}
                data-testid={`ai-agent-${agent.id}`}
              >
                {/* Gradient Border on Hover - Desktop only */}
                <div className={`hidden lg:block absolute inset-0 bg-gradient-to-br ${agent.gradient} rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 -z-10 blur-xl`} />
                
                {/* Card content - Horizontal on mobile, vertical on lg */}
                <div className="flex items-start gap-4 lg:block">
                  {/* Icon */}
                  <div className={`w-14 h-14 lg:w-16 lg:h-16 rounded-xl lg:rounded-2xl bg-gradient-to-br ${agent.gradient} flex items-center justify-center flex-shrink-0 lg:mb-6 group-hover:scale-105 lg:group-hover:scale-110 transition-transform duration-500`}>
                    <IconComponent className="w-7 h-7 lg:w-8 lg:h-8 text-white" strokeWidth={1.5} />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    {/* Title and Online indicator */}
                    <div className="flex items-center justify-between mb-2 lg:mb-3">
                      <h3 className="font-display text-lg lg:text-2xl text-obsidian">
                        {agent.title}
                      </h3>
                      {/* Online Indicator - Mobile inline */}
                      <div className="flex items-center gap-1.5 lg:hidden">
                        <div className="relative">
                          <div className="w-2 h-2 bg-green-500 rounded-full" />
                          <div className="absolute inset-0 w-2 h-2 bg-green-500 rounded-full animate-ping" />
                        </div>
                        <span className="font-mono text-[10px] text-green-600">Online</span>
                      </div>
                    </div>
                    
                    <p className="font-body text-sm lg:text-base text-obsidian/60 mb-3 lg:mb-6 leading-relaxed line-clamp-2 lg:line-clamp-none">
                      {agent.description}
                    </p>

                    {/* Features - Hidden on mobile, shown on lg */}
                    <div className="hidden lg:block space-y-2 mb-6">
                      {agent.features.map((feature, i) => (
                        <div key={i} className="flex items-center gap-2">
                          <div className={`w-1.5 h-1.5 rounded-full bg-gradient-to-r ${agent.gradient}`} />
                          <span className="font-body text-sm text-obsidian/50">{feature}</span>
                        </div>
                      ))}
                    </div>

                    {/* CTA */}
                    <div className="flex items-center gap-2 text-obsidian font-body font-medium text-sm lg:text-base group-hover:gap-3 lg:group-hover:gap-4 transition-all">
                      <span>Start Chat</span>
                      <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </div>
                </div>

                {/* Online Indicator - Desktop only, absolute positioned */}
                <div className="hidden lg:flex absolute top-6 right-6 items-center gap-2">
                  <div className="relative">
                    <div className="w-2 h-2 bg-green-500 rounded-full" />
                    <div className="absolute inset-0 w-2 h-2 bg-green-500 rounded-full animate-ping" />
                  </div>
                  <span className="font-mono text-xs text-green-600">Online</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Bottom CTA */}
        <div className="text-center mt-8 sm:mt-12 md:mt-16">
          <button 
            className="inline-flex items-center gap-2 md:gap-4 bg-obsidian text-white px-5 py-3 md:px-8 md:py-4 rounded-full font-body text-sm md:text-base hover:bg-obsidian/90 transition-colors cursor-pointer group"
            onClick={() => handleAgentClick('sales')}
          >
            <Bot className="w-4 h-4 md:w-5 md:h-5" />
            <span className="hidden sm:inline">Not sure which agent?</span>
            <span>Start with Sales</span>
            <ArrowRight className="w-4 h-4 md:w-5 md:h-5 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </div>
    </section>
  );
};

export default PremiumAIShowcase;
