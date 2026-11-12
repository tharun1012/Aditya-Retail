import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Store, Users, Award, Heart, Target, TrendingUp } from 'lucide-react';

const AboutPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <button
            onClick={() => navigate('/')}
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            ← Back to Store
          </button>
        </div>
      </div>

      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold mb-6">About Aditya Retail</h1>
          <p className="text-xl text-blue-100 max-w-3xl mx-auto">
            Your trusted partner for premium home appliances, powered by intelligent AI technology
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-16">
        {/* Our Story */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
          <div className="flex items-center gap-3 mb-6">
            <Store className="w-8 h-8 text-blue-600" />
            <h2 className="text-3xl font-bold text-gray-900">Our Story</h2>
          </div>
          <div className="prose max-w-none text-gray-700 space-y-4">
            <p className="text-lg">
              Aditya Retail was founded with a simple mission: to make premium home appliances accessible to every Indian household while providing an exceptional shopping experience powered by cutting-edge AI technology.
            </p>
            <p>
              As an authorized dealer of Bosch and Siemens home appliances, we bring you the finest German engineering combined with the convenience of modern e-commerce. Our platform is the first in India to integrate AI-powered shopping assistants that work 24/7 to help you make the perfect choice.
            </p>
            <p>
              From selecting the right dishwasher for your kitchen to troubleshooting your microwave, our intelligent agents are always ready to assist you with expert knowledge and personalized recommendations.
            </p>
          </div>
        </div>

        {/* Our Values */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          {[
            {
              icon: Heart,
              title: "Customer First",
              description: "Your satisfaction is our priority. We go the extra mile to ensure you get the best products and service.",
              color: "text-red-600 bg-red-50"
            },
            {
              icon: Award,
              title: "Quality Assured",
              description: "We partner only with premium brands like Bosch and Siemens to ensure you get products that last.",
              color: "text-blue-600 bg-blue-50"
            },
            {
              icon: TrendingUp,
              title: "Innovation Driven",
              description: "Our AI-powered platform brings you the future of shopping with personalized assistance and smart recommendations.",
              color: "text-purple-600 bg-purple-50"
            }
          ].map((value, index) => (
            <div key={index} className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
              <div className={`inline-flex items-center justify-center w-12 h-12 rounded-lg ${value.color} mb-4`}>
                <value.icon className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">{value.title}</h3>
              <p className="text-gray-600">{value.description}</p>
            </div>
          ))}
        </div>

        {/* What We Offer */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">What We Offer</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {[
              "Premium Bosch & Siemens appliances",
              "AI-powered shopping assistance",
              "24/7 technical support",
              "Genuine products with warranty",
              "Easy EMI options",
              "Free installation support",
              "Doorstep delivery across India",
              "Expert buying guidance"
            ].map((item, index) => (
              <div key={index} className="flex items-center gap-3">
                <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                <p className="text-gray-700">{item}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Our Commitment */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-lg p-8 text-white text-center">
          <Target className="w-12 h-12 mx-auto mb-4" />
          <h2 className="text-3xl font-bold mb-4">Our Commitment</h2>
          <p className="text-xl text-blue-100 max-w-3xl mx-auto mb-6">
            We're committed to transforming your home with premium appliances and exceptional service. Every product we sell, every interaction we have, is guided by our promise to deliver excellence.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => navigate('/')}
              className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
            >
              Shop Now
            </button>
            <button
              onClick={() => navigate('/contact')}
              className="bg-transparent border-2 border-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors"
            >
              Contact Us
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-12">
          {[
            { number: "10,000+", label: "Happy Customers" },
            { number: "95+", label: "Products Available" },
            { number: "24/7", label: "AI Support" },
            { number: "100%", label: "Genuine Products" }
          ].map((stat, index) => (
            <div key={index} className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">{stat.number}</div>
              <div className="text-gray-600">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AboutPage;
