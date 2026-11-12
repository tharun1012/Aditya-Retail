import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import {
  Target, RefreshCw, Play, Users, TrendingUp, MapPin, Search,
  CheckCircle, Clock, AlertTriangle, ArrowRight, Filter, Download,
  Twitter, Youtube, Linkedin, Instagram, Facebook, Globe, Zap
} from 'lucide-react';
import {
  BarChart, Bar, PieChart, Pie, Cell, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';


const LeadScrapingDashboard = () => {
  const [dashboard, setDashboard] = useState(null);
  const [leads, setLeads] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [runningJob, setRunningJob] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [filters, setFilters] = useState({ source: '', status: '', city: '' });

  useEffect(() => {
    fetchDashboard();
    fetchLeads();
    fetchAnalytics();
  }, []);

  const fetchDashboard = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/lead-scraping/dashboard`);
      if (response.ok) {
        const data = await response.json();
        setDashboard(data);
      }
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    }
  };

  const fetchLeads = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filters.source) params.append('source', filters.source);
      if (filters.status) params.append('status', filters.status);
      if (filters.city) params.append('city', filters.city);
      
      const response = await fetch(`${BACKEND_URL}/api/lead-scraping/leads?${params}`);
      if (response.ok) {
        const data = await response.json();
        setLeads(data.leads || []);
      }
    } catch (error) {
      console.error('Error fetching leads:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/lead-scraping/analytics`);
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  const runScrapingJob = async () => {
    try {
      setRunningJob(true);
      const response = await fetch(`${BACKEND_URL}/api/lead-scraping/run-sync`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`Scraping complete! Found ${data.total_found} leads, saved ${data.total_saved} new leads.`);
        fetchDashboard();
        fetchLeads();
        fetchAnalytics();
      } else {
        alert('Scraping job failed. Please check settings.');
      }
    } catch (error) {
      console.error('Error running scraping job:', error);
      alert('Error running scraping job');
    } finally {
      setRunningJob(false);
    }
  };

  const convertLead = async (leadId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/lead-scraping/leads/${leadId}/convert`, {
        method: 'POST'
      });
      
      if (response.ok) {
        alert('Lead converted to CRM successfully!');
        fetchLeads();
        fetchDashboard();
      }
    } catch (error) {
      console.error('Error converting lead:', error);
    }
  };

  const getSourceIcon = (source) => {
    switch (source) {
      case 'twitter': return <Twitter className="w-4 h-4" />;
      case 'instagram': return <Instagram className="w-4 h-4" />;
      case 'facebook': return <Facebook className="w-4 h-4" />;
      case 'youtube': return <Youtube className="w-4 h-4" />;
      case 'linkedin': return <Linkedin className="w-4 h-4" />;
      default: return <Globe className="w-4 h-4" />;
    }
  };

  const getSourceColor = (source) => {
    switch (source) {
      case 'twitter': return 'bg-black text-white';
      case 'instagram': return 'bg-gradient-to-r from-purple-500 to-pink-500 text-white';
      case 'facebook': return 'bg-blue-600 text-white';
      case 'youtube': return 'bg-red-600 text-white';
      case 'linkedin': return 'bg-blue-700 text-white';
      default: return 'bg-gray-600 text-white';
    }
  };

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

  if (loading && !dashboard) {
    return (
      <div className="min-h-screen bg-gray-50 p-6 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading lead scraping dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Target className="w-8 h-8 text-blue-600" />
              Autonomous Lead Generation
            </h1>
            <p className="text-gray-600 mt-1">AI-powered lead scraping from social media & directories</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => { fetchDashboard(); fetchLeads(); fetchAnalytics(); }}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
            <button
              onClick={runScrapingJob}
              disabled={runningJob}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 disabled:opacity-50"
            >
              {runningJob ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Run Scraping Now
                </>
              )}
            </button>
          </div>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-600 text-sm font-medium">Total Leads Found</h3>
              <Users className="w-8 h-8 text-blue-500" />
            </div>
            <p className="text-3xl font-bold text-gray-900">
              {dashboard?.overview?.total_leads || 0}
            </p>
            <p className="text-sm text-gray-500 mt-2">
              +{dashboard?.overview?.leads_today || 0} today
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-600 text-sm font-medium">Converted to CRM</h3>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
            <p className="text-3xl font-bold text-gray-900">
              {dashboard?.overview?.converted_leads || 0}
            </p>
            <p className="text-sm text-green-600 mt-2">
              {dashboard?.overview?.conversion_rate || 0}% conversion rate
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-600 text-sm font-medium">Active Sources</h3>
              <Zap className="w-8 h-8 text-yellow-500" />
            </div>
            <p className="text-3xl font-bold text-gray-900">
              {dashboard?.platform_status?.filter(p => p.is_enabled).length || 0}
            </p>
            <p className="text-sm text-gray-500 mt-2">
              of {dashboard?.platform_status?.length || 0} configured
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-600 text-sm font-medium">Scraping Status</h3>
              <Clock className="w-8 h-8 text-purple-500" />
            </div>
            <p className="text-3xl font-bold text-gray-900">
              {dashboard?.settings?.is_enabled ? 'Active' : 'Disabled'}
            </p>
            <p className="text-sm text-gray-500 mt-2">
              {dashboard?.settings?.scraping_frequency || 'daily'} frequency
            </p>
          </div>
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
              onClick={() => setActiveTab('leads')}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'leads'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Scraped Leads
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'analytics'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Analytics
            </button>
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Platform Status */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Platform Status</h3>
              <div className="space-y-3">
                {dashboard?.platform_status?.map((platform, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${getSourceColor(platform.platform)}`}>
                        {getSourceIcon(platform.platform)}
                      </div>
                      <span className="font-medium capitalize">{platform.platform}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      {platform.is_configured ? (
                        <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                          Configured
                        </span>
                      ) : (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                          Not Set
                        </span>
                      )}
                      {platform.is_enabled ? (
                        <CheckCircle className="w-5 h-5 text-green-500" />
                      ) : (
                        <AlertTriangle className="w-5 h-5 text-yellow-500" />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Leads by Source */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Leads by Source</h3>
              {dashboard?.leads_by_source && Object.keys(dashboard.leads_by_source).length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={Object.entries(dashboard.leads_by_source).map(([source, count]) => ({
                        name: source,
                        value: count
                      }))}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      label
                    >
                      {Object.keys(dashboard.leads_by_source).map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-64 flex items-center justify-center text-gray-500">
                  No leads scraped yet. Click "Run Scraping Now" to start.
                </div>
              )}
            </div>

            {/* Recent Jobs */}
            <div className="bg-white rounded-lg shadow-md p-6 lg:col-span-2">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Scraping Jobs</h3>
              {dashboard?.recent_jobs?.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full">
                    <thead>
                      <tr className="bg-gray-50">
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Time</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Found</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Saved</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Twitter</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Facebook</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">LinkedIn</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Others</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {dashboard.recent_jobs.map((job, idx) => (
                        <tr key={idx}>
                          <td className="px-4 py-3 text-sm text-gray-900">
                            {new Date(job.completed_at).toLocaleString()}
                          </td>
                          <td className="px-4 py-3 text-sm font-medium text-blue-600">{job.total_found}</td>
                          <td className="px-4 py-3 text-sm font-medium text-green-600">{job.total_saved}</td>
                          <td className="px-4 py-3 text-sm text-gray-600">{job.results?.twitter || 0}</td>
                          <td className="px-4 py-3 text-sm text-gray-600">{job.results?.facebook || 0}</td>
                          <td className="px-4 py-3 text-sm text-gray-600">{job.results?.linkedin || 0}</td>
                          <td className="px-4 py-3 text-sm text-gray-600">
                            {(job.results?.instagram || 0) + (job.results?.youtube || 0) + (job.results?.google_places || 0)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No scraping jobs run yet
                </div>
              )}
            </div>
          </div>
        )}

        {/* Leads Tab */}
        {activeTab === 'leads' && (
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            {/* Filters */}
            <div className="p-4 border-b bg-gray-50 flex flex-wrap gap-4">
              <select
                value={filters.source}
                onChange={(e) => setFilters(prev => ({ ...prev, source: e.target.value }))}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
              >
                <option value="">All Sources</option>
                <option value="twitter">Twitter</option>
                <option value="facebook">Facebook</option>
                <option value="instagram">Instagram</option>
                <option value="youtube">YouTube</option>
                <option value="linkedin">LinkedIn</option>
                <option value="google_places">Google Places</option>
              </select>
              
              <select
                value={filters.status}
                onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
              >
                <option value="">All Status</option>
                <option value="new">New</option>
                <option value="converted">Converted</option>
                <option value="suggested">Suggested</option>
              </select>
              
              <input
                type="text"
                placeholder="Filter by city..."
                value={filters.city}
                onChange={(e) => setFilters(prev => ({ ...prev, city: e.target.value }))}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
              />
              
              <button
                onClick={fetchLeads}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
              >
                <Filter className="w-4 h-4" />
                Apply Filters
              </button>
            </div>

            {/* Leads Table */}
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Source</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name / Business</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {leads.map((lead, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className={`inline-flex items-center gap-2 px-2 py-1 rounded-full text-xs ${getSourceColor(lead.source)}`}>
                          {getSourceIcon(lead.source)}
                          {lead.source}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-gray-900">{lead.name || lead.business_type || 'Unknown'}</div>
                        <div className="text-sm text-gray-500">{lead.username || lead.keyword_matched || ''}</div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        <div className="flex items-center gap-1">
                          <MapPin className="w-3 h-3" />
                          {lead.location || lead.city_matched || 'N/A'}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          lead.lead_type === 'b2b_business' ? 'bg-purple-100 text-purple-700' :
                          lead.lead_type === 'social_intent' ? 'bg-blue-100 text-blue-700' :
                          lead.lead_type === 'influencer' ? 'bg-pink-100 text-pink-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {lead.lead_type?.replace('_', ' ') || 'Unknown'}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-gray-200 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full ${
                                lead.score >= 70 ? 'bg-green-500' :
                                lead.score >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${lead.score || 0}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium">{lead.score || 0}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          lead.status === 'converted' ? 'bg-green-100 text-green-700' :
                          lead.status === 'new' ? 'bg-blue-100 text-blue-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {lead.status}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        {lead.status !== 'converted' && (
                          <button
                            onClick={() => convertLead(lead.id)}
                            className="px-3 py-1 bg-green-600 text-white text-xs rounded-lg hover:bg-green-700 flex items-center gap-1"
                          >
                            <ArrowRight className="w-3 h-3" />
                            Convert to CRM
                          </button>
                        )}
                        {lead.platform_url && (
                          <a
                            href={lead.platform_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="ml-2 text-blue-600 hover:underline text-xs"
                          >
                            View Profile
                          </a>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {leads.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                  No leads found. Run a scraping job to find new leads.
                </div>
              )}
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && analytics && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Daily Leads */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Leads Over Time (Last 7 Days)</h3>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={analytics.daily_leads || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Lead Type Distribution */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Lead Type Distribution</h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={analytics.type_distribution || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="type" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Top Cities */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Cities</h3>
              <div className="space-y-3">
                {analytics.top_cities?.map((city, idx) => (
                  <div key={idx} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-700">{city.city}</span>
                    </div>
                    <span className="font-medium text-gray-900">{city.count} leads</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Conversion Funnel */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Conversion Funnel</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                  <span className="text-blue-700">Total Scraped</span>
                  <span className="font-bold text-blue-700">{analytics.funnel?.total || 0}</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                  <span className="text-yellow-700">New / Pending</span>
                  <span className="font-bold text-yellow-700">{analytics.funnel?.new || 0}</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <span className="text-green-700">Converted to CRM</span>
                  <span className="font-bold text-green-700">{analytics.funnel?.converted || 0}</span>
                </div>
                <div className="mt-4 p-4 bg-gray-100 rounded-lg text-center">
                  <span className="text-gray-600">Overall Conversion Rate</span>
                  <p className="text-3xl font-bold text-green-600">{analytics.funnel?.conversion_rate || 0}%</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LeadScrapingDashboard;
