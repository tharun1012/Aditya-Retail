import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Play, Bot, Sparkles, Zap } from 'lucide-react';

const HeroBannerCarousel = ({ onCategorySelect }) => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isAutoPlay, setIsAutoPlay] = useState(true);

  const heroSlides = [
    {
      id: 1,
      title: "AI-Powered Shopping Experience",
      subtitle: "Get personalized recommendations from our intelligent sales agent",
      description: "🤖 Ask our AI about products, compare features, negotiate prices, and get expert advice - all in real-time!",
      ctaText: "Talk to AI Sales Agent",
      ctaAction: "ai_chat",
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      image: "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
      aiFeature: true
    },
    {
      id: 2,
      title: "Smart Kitchen Appliances",
      subtitle: "Premium Bosch, Siemens & Hindware Collection",
      description: "Discover the latest in kitchen technology with AI-powered product recommendations tailored to your needs",
      ctaText: "Explore Kitchen Range",
      ctaAction: "category",
      category: "Oven",
      background: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
      image: "https://adityaretail.com/wp-content/uploads/2025/03/Mixer.jpg",
      aiFeature: false
    },
    {
      id: 3,
      title: "AI Inventory Management",
      subtitle: "Real-time stock updates & smart recommendations",
      description: "⚡ Our AI monitors stock levels, predicts demand, and ensures your favorite products are always available",
      ctaText: "Check AI Stock Insights",
      ctaAction: "ai_chat",
      background: "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",
      image: "https://images.unsplash.com/photo-1586953208448-b95a79798f07?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
      aiFeature: true
    },
    {
      id: 4,
      title: "Intelligent Customer Service",
      subtitle: "24/7 AI support for all your needs",
      description: "🛠️ Get instant troubleshooting, service requests, and technical support from our AI service agent",
      ctaText: "Get AI Support",
      ctaAction: "ai_chat",
      background: "linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)",
      image: "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
      aiFeature: true
    },
    {
      id: 5,
      title: "Premium Home Appliances",
      subtitle: "Trusted brands, unbeatable prices",
      description: "Shop with confidence - our AI ensures you get the best deals and perfect products for your home",
      ctaText: "Shop Now",
      ctaAction: "category",
      category: "Washing Machine",
      background: "linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)",
      image: "https://adityaretail.com/wp-content/uploads/2025/03/Washing-Machine.jpg",
      aiFeature: false
    }
  ];

  useEffect(() => {
    let interval;
    if (isAutoPlay) {
      interval = setInterval(() => {
        setCurrentSlide(prev => (prev + 1) % heroSlides.length);
      }, 5000);
    }
    return () => clearInterval(interval);
  }, [isAutoPlay, heroSlides.length]);

  const nextSlide = () => {
    setCurrentSlide(prev => (prev + 1) % heroSlides.length);
  };

  const prevSlide = () => {
    setCurrentSlide(prev => (prev - 1 + heroSlides.length) % heroSlides.length);
  };

  const goToSlide = (index) => {
    setCurrentSlide(index);
  };

  const handleCTA = (slide) => {
    if (slide.ctaAction === "ai_chat") {
      // Trigger AI chat
      const event = new CustomEvent('openAIChat');
      window.dispatchEvent(event);
    } else if (slide.ctaAction === "category") {
      onCategorySelect(slide.category);
    }
  };

  const currentSlideData = heroSlides[currentSlide];

  return (
    <div className="relative h-[600px] overflow-hidden bg-gray-900">
      {/* Background Slides */}
      <div className="absolute inset-0">
        {heroSlides.map((slide, index) => (
          <div
            key={slide.id}
            className={`absolute inset-0 transition-all duration-700 ease-in-out ${
              index === currentSlide ? 'opacity-100 scale-100' : 'opacity-0 scale-105'
            }`}
            style={{ background: slide.background }}
          >
            {/* Background Image */}
            <div 
              className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-30"
              style={{ backgroundImage: `url(${slide.image})` }}
            />
            
            {/* Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-r from-black/60 via-black/30 to-transparent" />
          </div>
        ))}
      </div>

      {/* Content */}
      <div className="relative z-10 h-full flex items-center">
        <div className="max-w-7xl mx-auto px-4 w-full">
          <div className="max-w-3xl">
            {/* AI Badge */}
            {currentSlideData.aiFeature && (
              <div className="inline-flex items-center space-x-2 bg-blue-500/20 backdrop-blur-sm border border-blue-400/30 rounded-full px-4 py-2 mb-4 animate-pulse">
                <Bot className="w-5 h-5 text-blue-300" />
                <span className="text-blue-200 text-sm font-medium">AI-Powered Feature</span>
                <Sparkles className="w-4 h-4 text-yellow-300" />
              </div>
            )}

            {/* Title */}
            <h1 className="text-5xl lg:text-6xl font-bold text-white mb-6 leading-tight">
              {currentSlideData.title.split(' ').map((word, index) => (
                <span 
                  key={index}
                  className={`inline-block mr-4 ${
                    ['AI-Powered', 'Smart', 'AI', 'Intelligent', 'Premium'].includes(word) 
                      ? 'text-yellow-300 animate-bounce' 
                      : ''
                  }`}
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  {word}
                </span>
              ))}
            </h1>

            {/* Subtitle */}
            <p className="text-xl lg:text-2xl text-blue-100 mb-4 font-light">
              {currentSlideData.subtitle}
            </p>

            {/* Description */}
            <p className="text-lg text-gray-200 mb-8 leading-relaxed max-w-2xl">
              {currentSlideData.description}
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4">
              <button
                onClick={() => handleCTA(currentSlideData)}
                className="group bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300 transform hover:scale-105 hover:shadow-2xl flex items-center justify-center space-x-2"
              >
                {currentSlideData.aiFeature ? (
                  <Bot className="w-6 h-6 group-hover:animate-spin" />
                ) : (
                  <Play className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                )}
                <span>{currentSlideData.ctaText}</span>
                <Zap className="w-5 h-5 text-yellow-300" />
              </button>

              <button
                onClick={() => {
                  const event = new CustomEvent('openAIChat');
                  window.dispatchEvent(event);
                }}
                className="group bg-white/10 backdrop-blur-sm border border-white/20 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300 hover:bg-white/20 flex items-center justify-center space-x-2"
              >
                <Bot className="w-6 h-6 group-hover:rotate-12 transition-transform" />
                <span>Ask AI Assistant</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Controls */}
      <div className="absolute inset-0 z-20 flex items-center justify-between px-4 pointer-events-none">
        <button
          onClick={prevSlide}
          onMouseEnter={() => setIsAutoPlay(false)}
          onMouseLeave={() => setIsAutoPlay(true)}
          className="pointer-events-auto bg-white/10 backdrop-blur-sm border border-white/20 hover:bg-white/20 text-white p-3 rounded-full transition-all duration-300 transform hover:scale-110"
        >
          <ChevronLeft className="w-6 h-6" />
        </button>
        <button
          onClick={nextSlide}
          onMouseEnter={() => setIsAutoPlay(false)}
          onMouseLeave={() => setIsAutoPlay(true)}
          className="pointer-events-auto bg-white/10 backdrop-blur-sm border border-white/20 hover:bg-white/20 text-white p-3 rounded-full transition-all duration-300 transform hover:scale-110"
        >
          <ChevronRight className="w-6 h-6" />
        </button>
      </div>

      {/* Dots Indicator */}
      <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 z-20">
        <div className="flex space-x-3">
          {heroSlides.map((_, index) => (
            <button
              key={index}
              onClick={() => goToSlide(index)}
              onMouseEnter={() => setIsAutoPlay(false)}
              onMouseLeave={() => setIsAutoPlay(true)}
              className={`w-4 h-4 rounded-full transition-all duration-300 ${
                index === currentSlide
                  ? 'bg-white scale-125 shadow-lg'
                  : 'bg-white/40 hover:bg-white/60'
              }`}
            />
          ))}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="absolute bottom-0 left-0 w-full h-1 bg-black/20 z-20">
        <div 
          className="h-full bg-gradient-to-r from-yellow-400 to-red-500 transition-all duration-300 ease-linear"
          style={{ 
            width: `${((currentSlide + 1) / heroSlides.length) * 100}%` 
          }}
        />
      </div>

      {/* AI Features Floating Elements */}
      <div className="absolute top-20 right-20 z-10 hidden lg:block">
        <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-4 animate-float">
          <div className="flex items-center space-x-2">
            <Bot className="w-6 h-6 text-blue-300 animate-pulse" />
            <span className="text-white font-medium">5 AI Agents Active</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HeroBannerCarousel;