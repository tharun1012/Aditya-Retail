import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { useNavigate } from 'react-router-dom';
import {
  BarChart, Bar, LineChart, Line, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { Bot, TrendingUp, Clock, MessageSquare, Star, CheckCircle, ArrowLeft } from 'lucide-react';

const AIAgentsPerformance = () => {
  const navigate = useNavigate();
  const [agentsData, setAgentsData] = useState({});
  const [trends, setTrends] = useState([]);
  const [comparison, setComparison] = useState({});
  const [loading, setLoading] = useState(true);

  
  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // Fetch all AI agent data
      const [perfRes, trendsRes, compRes] = await Promise.all([
        fetch(`${BACKEND_URL}/api/admin/ai-agents/performance-summary`),
        fetch(`${BACKEND_URL}/api/admin/ai-agents/trends?days=30`),
        fetch(`${BACKEND_URL}/api/admin/ai-agents/comparison`)
      ]);

      const perfData = await perfRes.json();
      const trendsData = await trendsRes.json();
      const compData = await compRes.json();

      setAgentsData(perfData.data || {});
      setTrends(trendsData.data || []);
      setComparison(compData.data || {});
      setLoading(false);
    } catch (error) {
      console.error('Error fetching AI agents data:', error);
      // Set default empty values on error
      setAgentsData({});
      setTrends([]);
      setComparison({});
      setLoading(false);
    }
  };

  const agentColors = {
    sales_agent: '#3b82f6',
    service_agent: '#10b981',
    marketing_agent: '#f59e0b',
    delivery_agent: '#8b5cf6',
    stock_agent: '#ec4899'
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-xl">Loading AI agents performance...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
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
        <div className="mb-8">
          <h1 className="text-3xl font-bold">AI Agents Performance</h1>
          <p className="text-gray-600 mt-2">Monitor and analyze your AI agents' performance</p>
        </div>

        {/* Agent Cards */}
        <div className="grid grid-cols-5 gap-6 mb-8">
          {Object.entries(agentsData || {}).map(([key, agent]) => (
            <div key={key} className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <Bot className="w-10 h-10" style={{ color: agentColors[key] || '#000' }} />
                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Active</span>
              </div>
              <h3 className="font-bold text-lg mb-2">{agent?.name || 'Unknown Agent'}</h3>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Interactions:</span>
                  <span className="font-semibold">{agent?.total_interactions || 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Success Rate:</span>
                  <span className="font-semibold text-green-600">{agent?.success_rate || 0}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Satisfaction:</span>
                  <span className="font-semibold">{agent?.customer_satisfaction || 0}/5</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Detailed Metrics Row 1 */}
        <div className="grid grid-cols-3 gap-6 mb-6">
          {/* Sales Agent Details */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: agentColors.sales_agent }}></div>
              Sales AI - Detailed Metrics
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-green-500" />
                  <span className="text-sm">Revenue Generated</span>
                </div>
                <span className="font-bold">₹{(agentsData?.sales_agent?.revenue_attributed || 0).toLocaleString()}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div className="flex items-center gap-2">
                  <MessageSquare className="w-5 h-5 text-blue-500" />
                  <span className="text-sm">Leads Generated</span>
                </div>
                <span className="font-bold">{agentsData?.sales_agent?.leads_generated || 0}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span className="text-sm">Conversion Rate</span>
                </div>
                <span className="font-bold">{agentsData?.sales_agent?.conversion_rate || 0}%</span>
              </div>
            </div>
          </div>

          {/* Service Agent Details */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: agentColors.service_agent || '#000' }}></div>
              Service AI - Detailed Metrics
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span className="text-sm">Tickets Resolved</span>
                </div>
                <span className="font-bold">{agentsData?.service_agent?.tickets_resolved || 0}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div className="flex items-center gap-2">
                  <Clock className="w-5 h-5 text-orange-500" />
                  <span className="text-sm">Avg Resolution Time</span>
                </div>
                <span className="font-bold">{agentsData?.service_agent?.average_resolution_time || 0} min</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-red-500" />
                  <span className="text-sm">Escalation Rate</span>
                </div>
                <span className="font-bold">{agentsData?.service_agent?.escalation_rate || 0}%</span>
              </div>
            </div>
          </div>

          {/* Marketing Agent Details */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: agentColors.marketing_agent || '#000' }}></div>
              Marketing AI - Detailed Metrics
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div className="flex items-center gap-2">
                  <MessageSquare className="w-5 h-5 text-blue-500" />
                  <span className="text-sm">Emails Sent</span>
                </div>
                <span className="font-bold">{(agentsData?.marketing_agent?.emails_sent || 0).toLocaleString()}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div className="flex items-center gap-2">
                  <Star className="w-5 h-5 text-yellow-500" />
                  <span className="text-sm">Open Rate</span>
                </div>
                <span className="font-bold">{agentsData?.marketing_agent?.open_rate || 0}%</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span className="text-sm">Click-Through Rate</span>
                </div>
                <span className="font-bold">{agentsData?.marketing_agent?.click_through_rate || 0}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          {/* Activity Trends */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Agent Activity Trends (30 Days)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="sales_interactions" stroke={agentColors.sales_agent} name="Sales" />
                <Line type="monotone" dataKey="service_interactions" stroke={agentColors.service_agent} name="Service" />
                <Line type="monotone" dataKey="marketing_interactions" stroke={agentColors.marketing_agent} name="Marketing" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Comparison Radar */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Agent Comparison (Efficiency %)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={[
                { agent: 'Sales', value: comparison?.efficiency?.sales || 0 },
                { agent: 'Service', value: comparison?.efficiency?.service || 0 },
                { agent: 'Marketing', value: comparison?.efficiency?.marketing || 0 },
                { agent: 'Delivery', value: comparison?.efficiency?.delivery || 0 },
                { agent: 'Stock', value: comparison?.efficiency?.stock || 0 }
              ]}>
                <PolarGrid />
                <PolarAngleAxis dataKey="agent" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar name="Efficiency" dataKey="value" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Response Time Comparison */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Average Response Time Comparison (seconds)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={[
              { agent: 'Sales', time: comparison?.response_time?.sales || 0 },
              { agent: 'Service', time: comparison?.response_time?.service || 0 },
              { agent: 'Marketing', time: comparison?.response_time?.marketing || 0 },
              { agent: 'Delivery', time: comparison?.response_time?.delivery || 0 },
              { agent: 'Stock', time: comparison?.response_time?.stock || 0 }
            ]}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="agent" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="time" fill="#8b5cf6" name="Response Time (s)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default AIAgentsPerformance;
