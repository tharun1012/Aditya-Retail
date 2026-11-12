import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import {
  Sparkles, ChefHat, Zap, DollarSign, Users, Clock, Send, CheckCircle,
  ArrowRight, ArrowLeft, Home, Refrigerator, Loader, Mail, Phone, User
} from 'lucide-react';


const ExpertConsultation = ({ isOpen, onClose }) => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [consultationId, setConsultationId] = useState(null);
  const [options, setOptions] = useState(null);
  
  const [formData, setFormData] = useState({
    customer_name: '',
    email: '',
    phone: '',
    kitchen_size: 'medium',
    kitchen_dimensions: '',
    budget_min: 50000,
    budget_max: 200000,
    appliance_types: [],
    family_size: '3-4',
    cooking_frequency: 'daily',
    priority_factors: ['quality', 'energy_efficiency', 'price'],
    brand_preference: ['any'],
    energy_priority: 'important',
    aesthetic_preference: 'modern',
    special_requirements: ''
  });

  useEffect(() => {
    fetchOptions();
  }, []);

  const fetchOptions = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/consultation/options`);
      if (response.ok) {
        const data = await response.json();
        setOptions(data);
      }
    } catch (error) {
      console.error('Error fetching options:', error);
    }
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const toggleArrayItem = (field, item) => {
    setFormData(prev => {
      const current = prev[field] || [];
      if (current.includes(item)) {
        return { ...prev, [field]: current.filter(i => i !== item) };
      } else {
        return { ...prev, [field]: [...current, item] };
      }
    });
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/consultation/request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      if (response.ok) {
        const data = await response.json();
        setConsultationId(data.consultation_id);
        setSubmitted(true);
      } else {
        alert('Error submitting request. Please try again.');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error submitting request. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const totalSteps = 5;
  const progress = (step / totalSteps) * 100;

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden shadow-2xl">
        
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-6 text-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-white/20 rounded-lg">
                <Sparkles className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-xl font-bold">Expert Consultation</h2>
                <p className="text-blue-100 text-sm">Get personalized appliance recommendations</p>
              </div>
            </div>
            <button 
              onClick={onClose}
              className="text-white/80 hover:text-white text-2xl font-light"
            >
              ×
            </button>
          </div>
          
          {/* Progress Bar */}
          {!submitted && (
            <div className="mt-4">
              <div className="flex justify-between text-xs text-blue-200 mb-2">
                <span>Step {step} of {totalSteps}</span>
                <span>{Math.round(progress)}% Complete</span>
              </div>
              <div className="h-2 bg-white/20 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-white transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          
          {submitted ? (
            /* Success State */
            <div className="text-center py-8">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <CheckCircle className="w-10 h-10 text-green-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">Request Submitted!</h3>
              <p className="text-gray-600 mb-6">
                Our AI consultant is analyzing your requirements. You'll receive a detailed report at <strong>{formData.email}</strong> within 10-15 minutes.
              </p>
              <div className="bg-blue-50 p-4 rounded-lg text-left mb-6">
                <p className="text-sm text-blue-800">
                  <strong>What's Next?</strong>
                </p>
                <ul className="text-sm text-blue-700 mt-2 space-y-1">
                  <li>✓ AI analyzes your requirements</li>
                  <li>✓ Matches with best products from our catalog</li>
                  <li>✓ Calculates energy savings & total cost</li>
                  <li>✓ Generates detailed PDF report</li>
                  <li>✓ Emails you the comprehensive report</li>
                </ul>
              </div>
              <p className="text-sm text-gray-500">
                Consultation ID: <code className="bg-gray-100 px-2 py-1 rounded">{consultationId}</code>
              </p>
              <button
                onClick={onClose}
                className="mt-6 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Close
              </button>
            </div>
          ) : (
            <>
              {/* Step 1: Personal Info */}
              {step === 1 && (
                <div className="space-y-6">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                    <User className="w-5 h-5 text-blue-600" />
                    Your Information
                  </h3>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Full Name *</label>
                    <input
                      type="text"
                      value={formData.customer_name}
                      onChange={(e) => handleChange('customer_name', e.target.value)}
                      placeholder="Enter your name"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Email Address *</label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => handleChange('email', e.target.value)}
                      placeholder="your.email@example.com"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">Report will be sent to this email</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Phone Number (Optional)</label>
                    <input
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => handleChange('phone', e.target.value)}
                      placeholder="+91 98765 43210"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              )}

              {/* Step 2: Kitchen Details */}
              {step === 2 && (
                <div className="space-y-6">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                    <Home className="w-5 h-5 text-blue-600" />
                    Kitchen Details
                  </h3>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">Kitchen Size</label>
                    <div className="grid grid-cols-3 gap-3">
                      {options?.kitchen_sizes?.map(size => (
                        <button
                          key={size.value}
                          onClick={() => handleChange('kitchen_size', size.value)}
                          className={`p-4 border-2 rounded-lg text-center transition-all ${
                            formData.kitchen_size === size.value
                              ? 'border-blue-500 bg-blue-50 text-blue-700'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          <span className="block text-2xl mb-1">
                            {size.value === 'small' ? '🏠' : size.value === 'medium' ? '🏡' : '🏘️'}
                          </span>
                          <span className="text-sm font-medium">{size.label}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Kitchen Dimensions (Optional)</label>
                    <input
                      type="text"
                      value={formData.kitchen_dimensions}
                      onChange={(e) => handleChange('kitchen_dimensions', e.target.value)}
                      placeholder="e.g., 10x12 feet"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Family Size</label>
                      <select
                        value={formData.family_size}
                        onChange={(e) => handleChange('family_size', e.target.value)}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      >
                        {options?.family_sizes?.map(size => (
                          <option key={size.value} value={size.value}>{size.label}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Cooking Frequency</label>
                      <select
                        value={formData.cooking_frequency}
                        onChange={(e) => handleChange('cooking_frequency', e.target.value)}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      >
                        {options?.cooking_frequencies?.map(freq => (
                          <option key={freq.value} value={freq.value}>{freq.label}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {/* Step 3: Appliances Needed */}
              {step === 3 && (
                <div className="space-y-6">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                    <ChefHat className="w-5 h-5 text-blue-600" />
                    What Appliances Do You Need?
                  </h3>
                  <p className="text-gray-600 text-sm">Select all that apply</p>
                  
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    {options?.appliance_types?.map(appliance => (
                      <button
                        key={appliance.value}
                        onClick={() => toggleArrayItem('appliance_types', appliance.value)}
                        className={`p-4 border-2 rounded-lg text-center transition-all ${
                          formData.appliance_types.includes(appliance.value)
                            ? 'border-blue-500 bg-blue-50 text-blue-700'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <span className="text-2xl block mb-2">{appliance.icon}</span>
                        <span className="text-xs font-medium">{appliance.label}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Step 4: Budget & Preferences */}
              {step === 4 && (
                <div className="space-y-6">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                    <DollarSign className="w-5 h-5 text-blue-600" />
                    Budget & Preferences
                  </h3>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">Budget Range</label>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                      {options?.budget_ranges?.map(range => (
                        <button
                          key={range.label}
                          onClick={() => {
                            handleChange('budget_min', range.min);
                            handleChange('budget_max', range.max);
                          }}
                          className={`p-3 border-2 rounded-lg text-center transition-all ${
                            formData.budget_min === range.min && formData.budget_max === range.max
                              ? 'border-blue-500 bg-blue-50 text-blue-700'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          <span className="text-sm font-medium">{range.label}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">Brand Preference</label>
                    <div className="flex flex-wrap gap-2">
                      {options?.brands?.map(brand => (
                        <button
                          key={brand.value}
                          onClick={() => handleChange('brand_preference', [brand.value])}
                          className={`px-4 py-2 border-2 rounded-full text-sm transition-all ${
                            formData.brand_preference.includes(brand.value)
                              ? 'border-blue-500 bg-blue-50 text-blue-700'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          {brand.label}
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Energy Efficiency</label>
                      <select
                        value={formData.energy_priority}
                        onChange={(e) => handleChange('energy_priority', e.target.value)}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      >
                        {options?.energy_priorities?.map(ep => (
                          <option key={ep.value} value={ep.value}>{ep.label}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Design Style</label>
                      <select
                        value={formData.aesthetic_preference}
                        onChange={(e) => handleChange('aesthetic_preference', e.target.value)}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      >
                        {options?.aesthetic_preferences?.map(ap => (
                          <option key={ap.value} value={ap.value}>{ap.label}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {/* Step 5: Special Requirements */}
              {step === 5 && (
                <div className="space-y-6">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-blue-600" />
                    Any Special Requirements?
                  </h3>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Tell us more about what you're looking for
                    </label>
                    <textarea
                      value={formData.special_requirements}
                      onChange={(e) => handleChange('special_requirements', e.target.value)}
                      placeholder="e.g., I need appliances that are quiet, have smart features, match stainless steel finish, etc."
                      rows={4}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  {/* Summary */}
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-3">Summary</h4>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div className="text-gray-600">Kitchen:</div>
                      <div className="text-gray-900">{formData.kitchen_size}</div>
                      <div className="text-gray-600">Budget:</div>
                      <div className="text-gray-900">₹{formData.budget_min.toLocaleString()} - ₹{formData.budget_max.toLocaleString()}</div>
                      <div className="text-gray-600">Appliances:</div>
                      <div className="text-gray-900">{formData.appliance_types.length} selected</div>
                      <div className="text-gray-600">Email:</div>
                      <div className="text-gray-900">{formData.email}</div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer Navigation */}
        {!submitted && (
          <div className="px-6 py-4 bg-gray-50 border-t flex justify-between">
            <button
              onClick={() => setStep(Math.max(1, step - 1))}
              disabled={step === 1}
              className="px-4 py-2 text-gray-600 hover:text-gray-900 disabled:opacity-50 flex items-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </button>
            
            {step < totalSteps ? (
              <button
                onClick={() => setStep(step + 1)}
                disabled={
                  (step === 1 && (!formData.customer_name || !formData.email)) ||
                  (step === 3 && formData.appliance_types.length === 0)
                }
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
              >
                Next
                <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader className="w-4 h-4 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Get My Report
                  </>
                )}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ExpertConsultation;
