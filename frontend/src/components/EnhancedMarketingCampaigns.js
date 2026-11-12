import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { Mail, MessageSquare, Phone, Users, Target, TrendingUp, Zap, ShoppingCart, Split, Play, Pause, Edit, Trash2, PlusCircle, BarChart3 } from 'lucide-react';


const EnhancedMarketingCampaigns = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [activeTab, setActiveTab] = useState('campaigns');
  
  const [formData, setFormData] = useState({
    name: '',
    type: 'email',
    channels: ['email'],
    target_segment: 'all',
    custom_segment: {
      min_order_value: 0,
      max_order_value: null,
      last_purchase_days: null,
      category_interest: '',
      location: ''
    },
    subject: '',
    email_content: '',
    sms_content: '',
    whatsapp_content: '',
    enable_ab_testing: false,
    variant_a_subject: '',
    variant_b_subject: '',
    schedule_type: 'immediate',
    schedule_date: '',
    automation_trigger: 'none',
    cart_abandonment_delay: 60
  });

  const channelOptions = [
    { value: 'email', label: 'Email', icon: Mail, color: 'blue' },
    { value: 'sms', label: 'SMS', icon: MessageSquare, color: 'green' },
    { value: 'whatsapp', label: 'WhatsApp', icon: Phone, color: 'emerald' }
  ];

  const segmentOptions = [
    { value: 'all', label: 'All Customers' },
    { value: 'high_value', label: 'High Value Customers (₹10k+)' },
    { value: 'recent', label: 'Recent Customers (Last 30 days)' },
    { value: 'inactive', label: 'Inactive Customers (90+ days)' },
    { value: 'cart_abandoners', label: 'Cart Abandoners' },
    { value: 'first_time', label: 'First Time Buyers' },
    { value: 'custom', label: 'Custom Segment' }
  ];

  const automationTriggers = [
    { value: 'none', label: 'No Automation - Manual Send' },
    { value: 'cart_abandonment', label: 'Cart Abandonment (Auto-trigger)' },
    { value: 'post_purchase', label: 'Post Purchase Follow-up' },
    { value: 'birthday', label: 'Birthday Wishes' },
    { value: 'product_restock', label: 'Product Back in Stock' }
  ];

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/marketing-campaigns`);
      const data = await response.json();
      setCampaigns(data.campaigns || []);
    } catch (error) {
      console.error('Error fetching campaigns:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const method = selectedCampaign ? 'PUT' : 'POST';
      const url = selectedCampaign 
        ? `${BACKEND_URL}/api/marketing-campaigns/${selectedCampaign.id}`
        : `${BACKEND_URL}/api/marketing-campaigns`;

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        alert(selectedCampaign ? 'Campaign updated!' : 'Campaign created!');
        setShowCreateModal(false);
        resetForm();
        fetchCampaigns();
      }
    } catch (error) {
      console.error('Error saving campaign:', error);
      alert('Failed to save campaign');
    }
  };

  const handleLaunch = async (campaignId) => {
    if (!window.confirm('Launch this campaign now?')) return;
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/marketing-campaigns/${campaignId}/launch`, {
        method: 'POST'
      });
      
      if (response.ok) {
        alert('Campaign launched successfully!');
        fetchCampaigns();
      }
    } catch (error) {
      console.error('Error launching campaign:', error);
      alert('Failed to launch campaign');
    }
  };

  const resetForm = () => {
    setSelectedCampaign(null);
    setFormData({
      name: '',
      type: 'email',
      channels: ['email'],
      target_segment: 'all',
      custom_segment: {},
      subject: '',
      email_content: '',
      sms_content: '',
      whatsapp_content: '',
      enable_ab_testing: false,
      variant_a_subject: '',
      variant_b_subject: '',
      schedule_type: 'immediate',
      schedule_date: '',
      automation_trigger: 'none',
      cart_abandonment_delay: 60
    });
  };

  const handleChannelToggle = (channel) => {
    setFormData(prev => ({
      ...prev,
      channels: prev.channels.includes(channel)
        ? prev.channels.filter(c => c !== channel)
        : [...prev.channels, channel]
    }));
  };

  const getCampaignStatusColor = (status) => {
    const colors = {
      'draft': 'gray',
      'scheduled': 'yellow',
      'active': 'green',
      'paused': 'orange',
      'completed': 'blue'
    };
    return colors[status] || 'gray';
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <Target className="w-8 h-8 text-purple-600" />
          Enhanced Marketing Campaigns
        </h1>
        <p className="text-gray-600 mt-2">Multi-channel campaigns with automation, segmentation & A/B testing</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 mb-6 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('campaigns')}
          className={`px-4 py-2 font-medium ${activeTab === 'campaigns' ? 'border-b-2 border-purple-600 text-purple-600' : 'text-gray-500'}`}
        >
          Campaigns
        </button>
        <button
          onClick={() => setActiveTab('automation')}
          className={`px-4 py-2 font-medium ${activeTab === 'automation' ? 'border-b-2 border-purple-600 text-purple-600' : 'text-gray-500'}`}
        >
          Automation
        </button>
        <button
          onClick={() => setActiveTab('analytics')}
          className={`px-4 py-2 font-medium ${activeTab === 'analytics' ? 'border-b-2 border-purple-600 text-purple-600' : 'text-gray-500'}`}
        >
          Analytics
        </button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center gap-3">
            <div className="bg-blue-100 p-3 rounded-lg">
              <Mail className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Campaigns</p>
              <p className="text-2xl font-bold">{campaigns.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center gap-3">
            <div className="bg-green-100 p-3 rounded-lg">
              <Users className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Customers Reached</p>
              <p className="text-2xl font-bold">-</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center gap-3">
            <div className="bg-purple-100 p-3 rounded-lg">
              <TrendingUp className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Avg. Open Rate</p>
              <p className="text-2xl font-bold">-</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center gap-3">
            <div className="bg-orange-100 p-3 rounded-lg">
              <ShoppingCart className="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Conversions</p>
              <p className="text-2xl font-bold">-</p>
            </div>
          </div>
        </div>
      </div>

      {/* Campaigns Tab */}
      {activeTab === 'campaigns' && (
        <>
          {/* Create Button */}
          <div className="mb-6">
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 flex items-center gap-2"
            >
              <PlusCircle className="w-5 h-5" />
              Create New Campaign
            </button>
          </div>

          {/* Campaigns List */}
          <div className="grid grid-cols-1 gap-4">
            {campaigns.length === 0 ? (
              <div className="bg-white p-12 rounded-lg shadow text-center">
                <Target className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 text-lg mb-4">No campaigns yet</p>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700"
                >
                  Create Your First Campaign
                </button>
              </div>
            ) : (
              campaigns.map(campaign => (
                <div key={campaign.id} className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-gray-900 mb-2">{campaign.name}</h3>
                      <div className="flex gap-2 mb-3">
                        {campaign.channels?.map(channel => {
                          const channelInfo = channelOptions.find(c => c.value === channel);
                          const Icon = channelInfo?.icon || Mail;
                          return (
                            <span key={channel} className={`px-3 py-1 rounded-full text-xs font-medium bg-${channelInfo?.color}-100 text-${channelInfo?.color}-700`}>
                              <Icon className="w-3 h-3 inline mr-1" />
                              {channelInfo?.label}
                            </span>
                          );
                        })}
                        {campaign.enable_ab_testing && (
                          <span className="px-3 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-700">
                            <Split className="w-3 h-3 inline mr-1" />
                            A/B Test
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mb-2">
                        <strong>Target:</strong> {segmentOptions.find(s => s.value === campaign.target_segment)?.label}
                      </p>
                      <p className="text-sm text-gray-600">
                        <strong>Automation:</strong> {automationTriggers.find(a => a.value === campaign.automation_trigger)?.label}
                      </p>
                    </div>
                    
                    <div className="flex flex-col items-end gap-2">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium bg-${getCampaignStatusColor(campaign.status)}-100 text-${getCampaignStatusColor(campaign.status)}-700`}>
                        {campaign.status || 'draft'}
                      </span>
                      
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleLaunch(campaign.id)}
                          className="bg-green-600 text-white p-2 rounded hover:bg-green-700"
                          title="Launch Campaign"
                        >
                          <Play className="w-4 h-4" />
                        </button>
                        <button className="bg-blue-600 text-white p-2 rounded hover:bg-blue-700" title="View Analytics">
                          <BarChart3 className="w-4 h-4" />
                        </button>
                        <button className="bg-gray-600 text-white p-2 rounded hover:bg-gray-700" title="Edit">
                          <Edit className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </>
      )}

      {/* Automation Tab */}
      {activeTab === 'automation' && (
        <div className="bg-white p-8 rounded-lg shadow">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2 mb-2">
              <Zap className="w-6 h-6 text-yellow-500" />
              Marketing Automation
            </h2>
            <p className="text-gray-600">Set up automated campaigns triggered by customer behavior</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Cart Abandonment */}
            <div className="border-2 border-dashed border-gray-300 p-6 rounded-lg hover:border-purple-500 transition-colors">
              <ShoppingCart className="w-12 h-12 text-purple-600 mb-4" />
              <h3 className="text-lg font-bold mb-2">Cart Abandonment</h3>
              <p className="text-sm text-gray-600 mb-4">
                Automatically send reminders to customers who left items in their cart
              </p>
              <button className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 text-sm">
                Configure
              </button>
            </div>

            {/* Post Purchase */}
            <div className="border-2 border-dashed border-gray-300 p-6 rounded-lg hover:border-blue-500 transition-colors">
              <Mail className="w-12 h-12 text-blue-600 mb-4" />
              <h3 className="text-lg font-bold mb-2">Post-Purchase Follow-up</h3>
              <p className="text-sm text-gray-600 mb-4">
                Thank customers and request reviews after their purchase
              </p>
              <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm">
                Configure
              </button>
            </div>

            {/* Birthday Campaign */}
            <div className="border-2 border-dashed border-gray-300 p-6 rounded-lg hover:border-pink-500 transition-colors">
              <Users className="w-12 h-12 text-pink-600 mb-4" />
              <h3 className="text-lg font-bold mb-2">Birthday Campaigns</h3>
              <p className="text-sm text-gray-600 mb-4">
                Send special offers on customer birthdays
              </p>
              <button className="bg-pink-600 text-white px-4 py-2 rounded hover:bg-pink-700 text-sm">
                Configure
              </button>
            </div>

            {/* Product Restock */}
            <div className="border-2 border-dashed border-gray-300 p-6 rounded-lg hover:border-green-500 transition-colors">
              <TrendingUp className="w-12 h-12 text-green-600 mb-4" />
              <h3 className="text-lg font-bold mb-2">Product Restock Alerts</h3>
              <p className="text-sm text-gray-600 mb-4">
                Notify customers when out-of-stock products are available
              </p>
              <button className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 text-sm">
                Configure
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && (
        <div className="bg-white p-8 rounded-lg shadow">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Campaign Analytics</h2>
          <p className="text-gray-600 mb-4">Coming soon: Detailed campaign performance metrics</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="border-2 border-gray-200 p-6 rounded-lg text-center">
              <p className="text-4xl font-bold text-gray-300 mb-2">--</p>
              <p className="text-sm text-gray-600">Email Open Rate</p>
            </div>
            <div className="border-2 border-gray-200 p-6 rounded-lg text-center">
              <p className="text-4xl font-bold text-gray-300 mb-2">--</p>
              <p className="text-sm text-gray-600">Click-Through Rate</p>
            </div>
            <div className="border-2 border-gray-200 p-6 rounded-lg text-center">
              <p className="text-4xl font-bold text-gray-300 mb-2">--</p>
              <p className="text-sm text-gray-600">Conversion Rate</p>
            </div>
          </div>
        </div>
      )}

      {/* Create/Edit Campaign Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 sticky top-0 bg-white z-10">
              <h2 className="text-2xl font-bold text-gray-900">
                {selectedCampaign ? 'Edit Campaign' : 'Create New Campaign'}
              </h2>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-6">
              {/* Campaign Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Campaign Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  required
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-600"
                  placeholder="Summer Sale 2024"
                />
              </div>

              {/* Channels */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Channels <span className="text-red-500">*</span>
                </label>
                <div className="flex gap-4">
                  {channelOptions.map(channel => {
                    const Icon = channel.icon;
                    return (
                      <label key={channel.value} className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={formData.channels.includes(channel.value)}
                          onChange={() => handleChannelToggle(channel.value)}
                          className="w-4 h-4 text-purple-600"
                        />
                        <Icon className="w-5 h-5" />
                        <span>{channel.label}</span>
                      </label>
                    );
                  })}
                </div>
              </div>

              {/* Target Segment */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target Audience
                </label>
                <select
                  value={formData.target_segment}
                  onChange={(e) => setFormData({...formData, target_segment: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-600"
                >
                  {segmentOptions.map(option => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>

              {/* Email Content (if email channel selected) */}
              {formData.channels.includes('email') && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Subject <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.subject}
                    onChange={(e) => setFormData({...formData, subject: e.target.value})}
                    required
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-600"
                    placeholder="🎉 Exclusive Summer Sale - Up to 50% OFF!"
                  />
                  
                  <label className="block text-sm font-medium text-gray-700 mb-2 mt-4">
                    Email Content
                  </label>
                  <textarea
                    value={formData.email_content}
                    onChange={(e) => setFormData({...formData, email_content: e.target.value})}
                    rows="6"
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-600"
                    placeholder="Dear customer, we're excited to announce..."
                  />
                </div>
              )}

              {/* A/B Testing */}
              <div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.enable_ab_testing}
                    onChange={(e) => setFormData({...formData, enable_ab_testing: e.target.checked})}
                    className="w-4 h-4 text-purple-600"
                  />
                  <Split className="w-5 h-5 text-purple-600" />
                  <span className="font-medium">Enable A/B Testing</span>
                </label>
                {formData.enable_ab_testing && (
                  <div className="mt-4 grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">Variant A Subject</label>
                      <input
                        type="text"
                        value={formData.variant_a_subject}
                        onChange={(e) => setFormData({...formData, variant_a_subject: e.target.value})}
                        className="w-full px-4 py-2 border rounded-lg"
                        placeholder="Summer Sale - 50% OFF"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">Variant B Subject</label>
                      <input
                        type="text"
                        value={formData.variant_b_subject}
                        onChange={(e) => setFormData({...formData, variant_b_subject: e.target.value})}
                        className="w-full px-4 py-2 border rounded-lg"
                        placeholder="Don't Miss Out - Limited Time Offer!"
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Automation */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Automation Trigger
                </label>
                <select
                  value={formData.automation_trigger}
                  onChange={(e) => setFormData({...formData, automation_trigger: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-600"
                >
                  {automationTriggers.map(trigger => (
                    <option key={trigger.value} value={trigger.value}>{trigger.label}</option>
                  ))}
                </select>
              </div>

              {/* Form Actions */}
              <div className="flex justify-end gap-4 pt-4 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateModal(false);
                    resetForm();
                  }}
                  className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2"
                >
                  <Send className="w-4 h-4" />
                  {selectedCampaign ? 'Update Campaign' : 'Create Campaign'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedMarketingCampaigns;
