import React from 'react';
import { Sparkles, Clock, Mail, CheckCircle, ArrowRight } from 'lucide-react';

const PremiumConsultationCTA = ({ onConsultation }) => {
  const benefits = [
    'Personalized appliance recommendations',
    'Energy savings analysis',
    'Budget optimization tips',
    'Professional PDF report via email'
  ];

  return (
    <section className="relative py-12 sm:py-16 md:py-24 overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-obsidian">
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1920&q=80')] bg-cover bg-center opacity-10 md:opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b md:bg-gradient-to-r from-obsidian via-obsidian/95 to-obsidian/90" />
      </div>

      {/* Decorative Elements - Hidden on mobile */}
      <div className="hidden md:block absolute top-1/2 left-0 w-64 lg:w-96 h-64 lg:h-96 bg-gradient-to-r from-copper/20 to-yellow-500/20 rounded-full blur-3xl -translate-y-1/2" />
      <div className="hidden md:block absolute top-1/2 right-0 w-64 lg:w-96 h-64 lg:h-96 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-full blur-3xl -translate-y-1/2" />

      <div className="relative max-w-[1400px] mx-auto px-4 sm:px-6 md:px-12">
        {/* Stack vertically on mobile/tablet, 2-col grid on large screens */}
        <div className="flex flex-col gap-8 md:gap-12 lg:flex-row lg:items-center lg:gap-16">
          {/* Left Content */}
          <div className="space-y-5 md:space-y-6 text-center lg:text-left lg:flex-1">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 bg-copper/20 backdrop-blur-sm border border-copper/30 px-3 py-1.5 md:px-4 md:py-2 rounded-full">
              <Sparkles className="w-3 h-3 md:w-4 md:h-4 text-copper" />
              <span className="text-copper font-body text-xs md:text-sm">Most Popular Service</span>
            </div>

            {/* Headline */}
            <h2 className="font-display text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl text-white leading-tight tracking-tight">
              Free AI Kitchen
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-copper to-yellow-400">
                Consultation
              </span>
            </h2>

            {/* Description */}
            <p className="font-body text-sm sm:text-base md:text-lg text-white/70 max-w-lg mx-auto lg:mx-0 leading-relaxed">
              Answer a few questions about your kitchen and budget. Our AI expert delivers a personalized recommendation report to your inbox.
            </p>

            {/* Benefits - 2 columns on mobile */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-2 md:gap-3 text-left max-w-lg mx-auto lg:mx-0">
              {benefits.map((benefit, index) => (
                <div key={index} className="flex items-center gap-2 md:gap-3">
                  <CheckCircle className="w-4 h-4 md:w-5 md:h-5 text-copper flex-shrink-0" />
                  <span className="font-body text-sm md:text-base text-white/80">{benefit}</span>
                </div>
              ))}
            </div>

            {/* CTA Button */}
            <div className="pt-2 md:pt-4">
              <button
                onClick={onConsultation}
                className="group inline-flex items-center justify-center gap-2 md:gap-3 bg-white text-obsidian px-6 py-3 md:px-8 md:py-4 rounded-full font-body font-semibold text-sm md:text-base lg:text-lg hover:bg-platinum transition-all duration-500 ease-premium active:scale-95 w-full sm:w-auto"
                data-testid="consultation-cta-btn"
              >
                <Sparkles className="w-4 h-4 md:w-5 md:h-5" />
                Start Free Consultation
                <ArrowRight className="w-4 h-4 md:w-5 md:h-5 group-hover:translate-x-1 transition-transform" />
              </button>
            </div>
          </div>

          {/* Right - Stats Card */}
          <div className="relative w-full lg:flex-1 lg:max-w-md">
            <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl md:rounded-3xl p-5 sm:p-6 md:p-8 lg:p-12">
              {/* Time Badge */}
              <div className="flex items-center gap-3 mb-5 md:mb-8">
                <div className="w-10 h-10 md:w-12 md:h-12 rounded-full bg-copper/20 flex items-center justify-center flex-shrink-0">
                  <Clock className="w-5 h-5 md:w-6 md:h-6 text-copper" />
                </div>
                <div>
                  <div className="font-display text-xl md:text-2xl text-white">2 Minutes</div>
                  <div className="font-body text-xs md:text-sm text-white/50">to complete</div>
                </div>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-2 gap-3 md:gap-6 mb-5 md:mb-8">
                <div className="text-center p-3 sm:p-4 md:p-6 rounded-xl md:rounded-2xl bg-white/5 border border-white/10">
                  <div className="font-display text-2xl sm:text-3xl md:text-4xl text-white mb-1 md:mb-2">5,000+</div>
                  <div className="font-body text-xs md:text-sm text-white/50">Consultations</div>
                </div>
                <div className="text-center p-3 sm:p-4 md:p-6 rounded-xl md:rounded-2xl bg-white/5 border border-white/10">
                  <div className="font-display text-2xl sm:text-3xl md:text-4xl text-white mb-1 md:mb-2">98%</div>
                  <div className="font-body text-xs md:text-sm text-white/50">Satisfaction</div>
                </div>
              </div>

              {/* Report Preview */}
              <div className="flex items-center gap-3 md:gap-4 p-3 md:p-4 rounded-xl md:rounded-2xl bg-white/5 border border-white/10">
                <div className="w-10 h-10 md:w-12 md:h-12 rounded-lg md:rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                  <Mail className="w-5 h-5 md:w-6 md:h-6 text-white" />
                </div>
                <div className="min-w-0">
                  <div className="font-body font-medium text-sm md:text-base text-white truncate">Report in 10 mins</div>
                  <div className="font-body text-xs md:text-sm text-white/50 truncate">Detailed PDF with pricing</div>
                </div>
              </div>
            </div>

            {/* Decorative Badge */}
            <div className="absolute -top-3 -right-3 md:-top-4 md:-right-4 bg-gradient-to-r from-copper to-yellow-500 text-white px-3 py-1.5 md:px-4 md:py-2 rounded-full text-xs md:text-sm font-body font-medium shadow-lg">
              100% Free
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default PremiumConsultationCTA;
