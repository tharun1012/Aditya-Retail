import React from 'react';
import { Truck, Shield, Award, Star, CheckCircle, Package } from 'lucide-react';

const TrustBadges = () => {
  const badges = [
    { icon: Truck, title: "Assured Delivery", subtitle: "On Time, Every Time" },
    { icon: Star, title: "Quality Products", subtitle: "100% Genuine" },
    { icon: CheckCircle, title: "Trusted Partner", subtitle: "10+ Years" },
    { icon: Shield, title: "Secure Payment", subtitle: "Safe & Protected" },
    { icon: Award, title: "Best Brands", subtitle: "Bosch, Siemens & More" }
  ];

  return (
    <div className="bg-white py-8 border-b">
      <div className="max-w-7xl mx-auto px-4">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {badges.map((badge, index) => {
            const IconComponent = badge.icon;
            return (
              <div key={index} className="flex items-center space-x-3 p-4 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors">
                <div className="text-red-700 bg-red-50 p-2 rounded-full">
                  <IconComponent className="w-6 h-6" />
                </div>
                <div>
                  <div className="font-semibold text-gray-800">{badge.title}</div>
                  <div className="text-sm text-gray-600">{badge.subtitle}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default TrustBadges;