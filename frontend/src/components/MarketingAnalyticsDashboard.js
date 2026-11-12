import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { useNavigate } from 'react-router-dom';
import {
  TrendingUp, DollarSign, Users, Target, BarChart3, 
  PieChart, Activity, ArrowUp, ArrowDown, RefreshCw, ArrowLeft
} from 'lucide-react';
import {
  BarChart, Bar, LineChart, Line, PieChart as RechartsPie, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';


const MarketingAnalyticsDashboard = () => {
  const navigate = useNavigate();
  const [campaignData, setCampaignData] = useState(null);
  const [channelData, setChannelData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      
      // Fetch campaign performance
      const campaignRes = await fetch(`${BACKEND_URL}/api/marketing-analytics/campaign-performance`);
      const campaignJson = await campaignRes.json();
      setCampaignData(campaignJson);
      
      // Fetch channel performance
      const channelRes = await fetch(`${BACKEND_URL}/api/marketing-analytics/channel-performance`);
      const channelJson = await channelRes.json();
      setChannelData(channelJson);
      
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4'];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading marketing analytics...</p>
        </div>
      </div>
    );
  }

  const summary = campaignData?.summary || {};

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Back Button */}
        <button
          onClick={() => navigate('/admin')}
          className="flex items-center px-4 py-2 mb-6 text-gray-700 bg-white hover:bg-gray-100 rounded-lg transition-all border border-gray-300 hover:border-gray-400 shadow-sm"
          data-testid="back-to-dashboard-btn"
        >
          <ArrowLeft className="h-5 w-5 mr-2" />
          <span className="font-medium">Back to Dashboard</span>
        </button>

        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Marketing Analytics</h1>
            <p className="text-gray-600 mt-1">Campaign performance, ROI, and channel insights</p>
          </div>
          <button
            onClick={fetchAnalytics}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'overview'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('campaigns')}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'campaigns'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Campaigns
            </button>
            <button
              onClick={() => setActiveTab('channels')}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'channels'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Channels
            </button>
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-gray-600 text-sm font-medium">Total Budget</h3>
                  <DollarSign className="w-8 h-8 text-blue-500" />
                </div>
                <p className="text-3xl font-bold text-gray-900">
                  ₹{summary.total_budget?.toLocaleString() || 0}
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  Across {summary.total_campaigns || 0} campaigns
                </p>
              </div>

              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-gray-600 text-sm font-medium">Total Leads</h3>
                  <Users className="w-8 h-8 text-green-500" />
                </div>
                <p className="text-3xl font-bold text-gray-900">
                  {summary.total_leads || 0}
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  ₹{summary.avg_cost_per_lead?.toLocaleString() || 0} avg CPL
                </p>
              </div>

              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-gray-600 text-sm font-medium">Conversions</h3>
                  <Target className="w-8 h-8 text-orange-500" />
                </div>
                <p className="text-3xl font-bold text-gray-900">
                  {summary.total_conversions || 0}
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  {summary.avg_conversion_rate || 0}% conversion rate
                </p>
              </div>

              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-gray-600 text-sm font-medium">ROI</h3>
                  <TrendingUp className="w-8 h-8 text-purple-500" />
                </div>
                <p className="text-3xl font-bold text-gray-900">
                  {summary.overall_roi?.toFixed(1) || 0}%
                </p>
                <div className="flex items-center mt-2 text-green-600 text-sm">
                  <ArrowUp className="w-4 h-4 mr-1" />
                  <span>Revenue: ₹{summary.total_revenue?.toLocaleString() || 0}</span>
                </div>
              </div>
            </div>

            {/* Channel Performance Chart */}
            {channelData?.channels && (
              <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                <h3 className="text-xl font-bold text-gray-900 mb-6">Channel Performance</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={channelData.channels}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="channel" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="leads" fill="#3b82f6" name="Leads" />
                    <Bar dataKey="conversions" fill="#10b981" name="Conversions" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </>
        )}

        {/* Campaigns Tab */}
        {activeTab === 'campaigns' && (
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Campaign
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Budget
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Leads
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      CPL
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Conv. Rate
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Revenue
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      ROI
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {campaignData?.campaigns?.map((campaign, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-gray-900">
                          {campaign.campaign_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {campaign.product_name?.substring(0, 40)}...
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ₹{campaign.budget?.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {campaign.leads}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ₹{campaign.cost_per_lead?.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {campaign.conversion_rate}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ₹{campaign.revenue?.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`text-sm font-medium ${
                          campaign.roi > 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {campaign.roi > 0 ? '+' : ''}{campaign.roi}%
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          campaign.status === 'active' 
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {campaign.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Channels Tab */}
        {activeTab === 'channels' && channelData?.channels && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Channel Cards */}
            <div className="space-y-4">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Channel Performance</h3>
              {channelData.channels.map((channel, idx) => (
                <div key={idx} className="bg-white rounded-lg shadow-md p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-lg font-semibold text-gray-900">{channel.channel}</h4>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      channel.quality_rating === 'High' ? 'bg-green-100 text-green-800' :
                      channel.quality_rating === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {channel.quality_rating} Quality
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Leads</p>
                      <p className="text-2xl font-bold text-gray-900">{channel.leads}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Conv. Rate</p>
                      <p className="text-2xl font-bold text-gray-900">{channel.conversion_rate}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Revenue</p>
                      <p className="text-2xl font-bold text-gray-900">₹{(channel.revenue / 1000).toFixed(0)}K</p>
                    </div>
                  </div>
                  
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <p className="text-sm text-gray-600">
                      Avg Revenue per Lead: <span className="font-semibold">₹{channel.avg_revenue_per_lead?.toLocaleString()}</span>
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Channel Distribution Pie Chart */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-6">Lead Distribution</h3>
              <ResponsiveContainer width="100%" height={400}>
                <RechartsPie>
                  <Pie
                    data={channelData.channels}
                    dataKey="leads"
                    nameKey="channel"
                    cx="50%"
                    cy="50%"
                    outerRadius={120}
                    label
                  >
                    {channelData.channels.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </RechartsPie>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MarketingAnalyticsDashboard;
