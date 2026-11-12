import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { heroBanners } from '../data/mockData';

const HeroBanners = ({ onCategorySelect }) => {
  const [currentSlide, setCurrentSlide] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % heroBanners.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % heroBanners.length);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + heroBanners.length) % heroBanners.length);
  };

  return (
    <div className="bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {heroBanners.map((banner, index) => (
            <div
              key={banner.id}
              className="relative overflow-hidden rounded-xl bg-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 cursor-pointer"
              onClick={() => {
                const category = banner.link.split('/')[2];
                if (category === 'kitchen-appliances') onCategorySelect('Oven');
                else if (category === 'washing-machine') onCategorySelect('Washing Machine');
                else if (category === 'chimney') onCategorySelect('Chimney');
                else if (category === 'oven') onCategorySelect('Oven');
              }}
            >
              <div className="aspect-video relative">
                <img
                  src={banner.image}
                  alt={`${banner.title} - ${banner.description || 'Promotional banner'} - Aditya Retail`}
                  loading="eager"
                  decoding="async"
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
                <div className="absolute bottom-4 left-4 right-4 text-white">
                  <h3 className="text-lg font-bold mb-2 leading-tight">
                    {banner.title.split(' ').map((word, idx) => 
                      ['DEALS', 'MORE', 'SMART', 'OVENS'].includes(word) ? 
                      <span key={idx} className="text-yellow-400">{word} </span> : 
                      <span key={idx}>{word} </span>
                    )}
                  </h3>
                  <button className="bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-red-800 transition-colors flex items-center space-x-2">
                    <span>{banner.subtitle}</span>
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Carousel Indicators */}
        <div className="flex justify-center mt-6 space-x-2">
          {heroBanners.map((_, index) => (
            <button
              key={index}
              className={`w-3 h-3 rounded-full transition-colors ${
                index === currentSlide ? 'bg-red-700' : 'bg-gray-300'
              }`}
              onClick={() => setCurrentSlide(index)}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default HeroBanners;