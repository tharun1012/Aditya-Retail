import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { useNavigate } from 'react-router-dom';
import {
  Settings, Key, Globe, Shield, Save, RefreshCw, CheckCircle, XCircle,
  Eye, EyeOff, AlertTriangle, Zap, Target, MapPin, Search, Users,
  Twitter, Youtube, Linkedin, Instagram, Facebook, TrendingUp, ArrowLeft
} from 'lucide-react';


const AdminSettings = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('ad-platforms');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);
  
  // Platform credentials state
  const [googleAds, setGoogleAds] = useState({
    client_id: '', client_secret: '', developer_token: '', customer_id: '', refresh_token: '', is_enabled: false
  });
  const [facebookAds, setFacebookAds] = useState({
    app_id: '', app_secret: '', access_token: '', ad_account_id: '', page_id: '', is_enabled: false
  });
  const [twitter, setTwitter] = useState({
    api_key: '', api_secret: '', access_token: '', access_token_secret: '', bearer_token: '', is_enabled: false
  });
  const [instagram, setInstagram] = useState({
    access_token: '', business_account_id: '', is_enabled: false
  });
  const [youtube, setYoutube] = useState({
    api_key: '', client_id: '', client_secret: '', channel_id: '', is_enabled: false
  });
  const [linkedin, setLinkedin] = useState({
    client_id: '', client_secret: '', access_token: '', organization_id: '', is_enabled: false
  });
  
  // Lead scraping settings
  const [leadScraping, setLeadScraping] = useState({
    is_enabled: false,
    target_cities: [],
    keywords: [],
    business_types: [],
    scraping_frequency: 'daily',
    max_leads_per_day: 50,
    auto_follow_up: true
  });
  
  const [availableCities, setAvailableCities] = useState({ metro: [], tier2: [] });
  const [availableKeywords, setAvailableKeywords] = useState([]);
  const [availableBusinessTypes, setAvailableBusinessTypes] = useState([]);
  const [showSecrets, setShowSecrets] = useState({});

  useEffect(() => {
    fetchAllSettings();
    fetchConfigOptions();
  }, []);

  const fetchAllSettings = async () => {
    try {
      setLoading(true);
      
      // Fetch all platform settings
      const [googleRes, fbRes, twitterRes, instaRes, ytRes, linkedinRes, scrapingRes] = await Promise.all([
        fetch(`${BACKEND_URL}/api/admin-settings/google-ads`),
        fetch(`${BACKEND_URL}/api/admin-settings/facebook-ads`),
        fetch(`${BACKEND_URL}/api/admin-settings/twitter`),
        fetch(`${BACKEND_URL}/api/admin-settings/instagram`),
        fetch(`${BACKEND_URL}/api/admin-settings/youtube`),
        fetch(`${BACKEND_URL}/api/admin-settings/linkedin`),
        fetch(`${BACKEND_URL}/api/admin-settings/lead-scraping`)
      ]);
      
      if (googleRes.ok) {
        const data = await googleRes.json();
        setGoogleAds(prev => ({ ...prev, ...data, is_enabled: data.is_enabled || false }));
      }
      if (fbRes.ok) {
        const data = await fbRes.json();
        setFacebookAds(prev => ({ ...prev, ...data, is_enabled: data.is_enabled || false }));
      }
      if (twitterRes.ok) {
        const data = await twitterRes.json();
        setTwitter(prev => ({ ...prev, ...data, is_enabled: data.is_enabled || false }));
      }
      if (instaRes.ok) {
        const data = await instaRes.json();
        setInstagram(prev => ({ ...prev, ...data, is_enabled: data.is_enabled || false }));
      }
      if (ytRes.ok) {
        const data = await ytRes.json();
        setYoutube(prev => ({ ...prev, ...data, is_enabled: data.is_enabled || false }));
      }
      if (linkedinRes.ok) {
        const data = await linkedinRes.json();
        setLinkedin(prev => ({ ...prev, ...data, is_enabled: data.is_enabled || false }));
      }
      if (scrapingRes.ok) {
        const data = await scrapingRes.json();
        setLeadScraping(data);
      }
      
    } catch (error) {
      console.error('Error fetching settings:', error);
      showMessage('Error loading settings', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchConfigOptions = async () => {
    try {
      const [citiesRes, keywordsRes, businessRes] = await Promise.all([
        fetch(`${BACKEND_URL}/api/lead-scraping/config/cities`),
        fetch(`${BACKEND_URL}/api/lead-scraping/config/keywords`),
        fetch(`${BACKEND_URL}/api/lead-scraping/config/business-types`)
      ]);
      
      if (citiesRes.ok) {
        const data = await citiesRes.json();
        setAvailableCities({ metro: data.metro_cities, tier2: data.tier2_cities });
      }
      if (keywordsRes.ok) {
        const data = await keywordsRes.json();
        setAvailableKeywords(data.keywords);
      }
      if (businessRes.ok) {
        const data = await businessRes.json();
        setAvailableBusinessTypes(data.business_types);
      }
    } catch (error) {
      console.error('Error fetching config options:', error);
    }
  };

  const showMessage = (text, type = 'success') => {
    setMessage({ text, type });
    setTimeout(() => setMessage(null), 3000);
  };

  const saveCredentials = async (platform, data, endpoint) => {
    try {
      setSaving(true);
      const response = await fetch(`${BACKEND_URL}/api/admin-settings/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      
      if (response.ok) {
        showMessage(`${platform} credentials saved successfully`);
      } else {
        showMessage(`Failed to save ${platform} credentials`, 'error');
      }
    } catch (error) {
      showMessage(`Error saving ${platform} credentials`, 'error');
    } finally {
      setSaving(false);
    }
  };

  const saveLeadScrapingSettings = async () => {
    try {
      setSaving(true);
      const response = await fetch(`${BACKEND_URL}/api/admin-settings/lead-scraping`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(leadScraping)
      });
      
      if (response.ok) {
        showMessage('Lead scraping settings saved successfully');
      } else {
        showMessage('Failed to save lead scraping settings', 'error');
      }
    } catch (error) {
      showMessage('Error saving settings', 'error');
    } finally {
      setSaving(false);
    }
  };

  const testConnection = async (platform) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/admin-settings/test-connection/${platform}`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const data = await response.json();
        showMessage(`${platform} connection test: ${data.message}`);
      } else {
        showMessage(`${platform} connection test failed`, 'error');
      }
    } catch (error) {
      showMessage(`Error testing ${platform} connection`, 'error');
    }
  };

  const toggleSecret = (field) => {
    setShowSecrets(prev => ({ ...prev, [field]: !prev[field] }));
  };

  const CredentialInput = ({ label, value, onChange, type = 'text', placeholder, secretKey }) => (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <div className="relative">
        <input
          type={secretKey && !showSecrets[secretKey] ? 'password' : 'text'}
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
        {secretKey && (
          <button
            type="button"
            onClick={() => toggleSecret(secretKey)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
          >
            {showSecrets[secretKey] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        )}
      </div>
    </div>
  );

  const PlatformCard = ({ title, icon: Icon, color, isEnabled, onToggle, onSave, onTest, children }) => (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${color}`}>
            <Icon className="w-6 h-6 text-white" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        </div>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={isEnabled}
              onChange={(e) => onToggle(e.target.checked)}
              className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-600">Enabled</span>
          </label>
          {isEnabled && (
            <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full flex items-center gap-1">
              <CheckCircle className="w-3 h-3" /> Active
            </span>
          )}
        </div>
      </div>
      
      <div className="space-y-4">
        {children}
      </div>
      
      <div className="flex gap-3 mt-6 pt-4 border-t border-gray-200">
        <button
          onClick={onSave}
          disabled={saving}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 disabled:opacity-50"
        >
          <Save className="w-4 h-4" />
          Save
        </button>
        <button
          onClick={onTest}
          className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center gap-2"
        >
          <Zap className="w-4 h-4" />
          Test Connection
        </button>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
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
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Settings className="w-8 h-8 text-blue-600" />
            Admin Settings
          </h1>
          <p className="text-gray-600 mt-1">Manage API credentials and lead generation settings</p>
        </div>

        {/* Message */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg flex items-center gap-2 ${
            message.type === 'error' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
          }`}>
            {message.type === 'error' ? <XCircle className="w-5 h-5" /> : <CheckCircle className="w-5 h-5" />}
            {message.text}
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="flex border-b overflow-x-auto">
            <button
              onClick={() => setActiveTab('ad-platforms')}
              className={`px-6 py-3 font-medium whitespace-nowrap transition-colors ${
                activeTab === 'ad-platforms'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Globe className="w-4 h-4 inline mr-2" />
              Ad Platforms
            </button>
            <button
              onClick={() => setActiveTab('social-media')}
              className={`px-6 py-3 font-medium whitespace-nowrap transition-colors ${
                activeTab === 'social-media'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Users className="w-4 h-4 inline mr-2" />
              Social Media APIs
            </button>
            <button
              onClick={() => setActiveTab('lead-scraping')}
              className={`px-6 py-3 font-medium whitespace-nowrap transition-colors ${
                activeTab === 'lead-scraping'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Target className="w-4 h-4 inline mr-2" />
              Lead Scraping
            </button>
          </div>
        </div>

        {/* Ad Platforms Tab */}
        {activeTab === 'ad-platforms' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Google Ads */}
            <PlatformCard
              title="Google Ads"
              icon={Globe}
              color="bg-blue-500"
              isEnabled={googleAds.is_enabled}
              onToggle={(checked) => setGoogleAds(prev => ({ ...prev, is_enabled: checked }))}
              onSave={() => saveCredentials('Google Ads', googleAds, 'google-ads')}
              onTest={() => testConnection('google_ads')}
            >
              <CredentialInput
                label="Client ID"
                value={googleAds.client_id}
                onChange={(v) => setGoogleAds(prev => ({ ...prev, client_id: v }))}
                placeholder="Enter Google Ads Client ID"
              />
              <CredentialInput
                label="Client Secret"
                value={googleAds.client_secret}
                onChange={(v) => setGoogleAds(prev => ({ ...prev, client_secret: v }))}
                placeholder="Enter Client Secret"
                secretKey="google_secret"
              />
              <CredentialInput
                label="Developer Token"
                value={googleAds.developer_token}
                onChange={(v) => setGoogleAds(prev => ({ ...prev, developer_token: v }))}
                placeholder="Enter Developer Token"
                secretKey="google_dev_token"
              />
              <CredentialInput
                label="Customer ID"
                value={googleAds.customer_id}
                onChange={(v) => setGoogleAds(prev => ({ ...prev, customer_id: v }))}
                placeholder="e.g., 123-456-7890"
              />
            </PlatformCard>

            {/* Facebook Ads */}
            <PlatformCard
              title="Facebook / Meta Ads"
              icon={Facebook}
              color="bg-blue-600"
              isEnabled={facebookAds.is_enabled}
              onToggle={(checked) => setFacebookAds(prev => ({ ...prev, is_enabled: checked }))}
              onSave={() => saveCredentials('Facebook Ads', facebookAds, 'facebook-ads')}
              onTest={() => testConnection('facebook_ads')}
            >
              <CredentialInput
                label="App ID"
                value={facebookAds.app_id}
                onChange={(v) => setFacebookAds(prev => ({ ...prev, app_id: v }))}
                placeholder="Enter Facebook App ID"
              />
              <CredentialInput
                label="App Secret"
                value={facebookAds.app_secret}
                onChange={(v) => setFacebookAds(prev => ({ ...prev, app_secret: v }))}
                placeholder="Enter App Secret"
                secretKey="fb_secret"
              />
              <CredentialInput
                label="Access Token"
                value={facebookAds.access_token}
                onChange={(v) => setFacebookAds(prev => ({ ...prev, access_token: v }))}
                placeholder="Enter Access Token"
                secretKey="fb_token"
              />
              <CredentialInput
                label="Ad Account ID"
                value={facebookAds.ad_account_id}
                onChange={(v) => setFacebookAds(prev => ({ ...prev, ad_account_id: v }))}
                placeholder="e.g., act_123456789"
              />
              <CredentialInput
                label="Page ID"
                value={facebookAds.page_id}
                onChange={(v) => setFacebookAds(prev => ({ ...prev, page_id: v }))}
                placeholder="Enter Facebook Page ID"
              />
            </PlatformCard>
          </div>
        )}

        {/* Social Media APIs Tab */}
        {activeTab === 'social-media' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Twitter */}
            <PlatformCard
              title="Twitter / X"
              icon={Twitter}
              color="bg-black"
              isEnabled={twitter.is_enabled}
              onToggle={(checked) => setTwitter(prev => ({ ...prev, is_enabled: checked }))}
              onSave={() => saveCredentials('Twitter', twitter, 'twitter')}
              onTest={() => testConnection('twitter')}
            >
              <CredentialInput
                label="API Key"
                value={twitter.api_key}
                onChange={(v) => setTwitter(prev => ({ ...prev, api_key: v }))}
                placeholder="Enter API Key"
                secretKey="twitter_key"
              />
              <CredentialInput
                label="API Secret"
                value={twitter.api_secret}
                onChange={(v) => setTwitter(prev => ({ ...prev, api_secret: v }))}
                placeholder="Enter API Secret"
                secretKey="twitter_secret"
              />
              <CredentialInput
                label="Bearer Token"
                value={twitter.bearer_token}
                onChange={(v) => setTwitter(prev => ({ ...prev, bearer_token: v }))}
                placeholder="Enter Bearer Token"
                secretKey="twitter_bearer"
              />
              <CredentialInput
                label="Access Token"
                value={twitter.access_token}
                onChange={(v) => setTwitter(prev => ({ ...prev, access_token: v }))}
                placeholder="Enter Access Token"
                secretKey="twitter_access"
              />
            </PlatformCard>

            {/* Instagram */}
            <PlatformCard
              title="Instagram"
              icon={Instagram}
              color="bg-gradient-to-r from-purple-500 to-pink-500"
              isEnabled={instagram.is_enabled}
              onToggle={(checked) => setInstagram(prev => ({ ...prev, is_enabled: checked }))}
              onSave={() => saveCredentials('Instagram', instagram, 'instagram')}
              onTest={() => testConnection('instagram')}
            >
              <CredentialInput
                label="Access Token"
                value={instagram.access_token}
                onChange={(v) => setInstagram(prev => ({ ...prev, access_token: v }))}
                placeholder="Enter Instagram Access Token"
                secretKey="insta_token"
              />
              <CredentialInput
                label="Business Account ID"
                value={instagram.business_account_id}
                onChange={(v) => setInstagram(prev => ({ ...prev, business_account_id: v }))}
                placeholder="Enter Business Account ID"
              />
              <p className="text-sm text-gray-500 mt-2">
                <AlertTriangle className="w-4 h-4 inline mr-1" />
                Requires Facebook Business integration
              </p>
            </PlatformCard>

            {/* YouTube */}
            <PlatformCard
              title="YouTube"
              icon={Youtube}
              color="bg-red-600"
              isEnabled={youtube.is_enabled}
              onToggle={(checked) => setYoutube(prev => ({ ...prev, is_enabled: checked }))}
              onSave={() => saveCredentials('YouTube', youtube, 'youtube')}
              onTest={() => testConnection('youtube')}
            >
              <CredentialInput
                label="API Key"
                value={youtube.api_key}
                onChange={(v) => setYoutube(prev => ({ ...prev, api_key: v }))}
                placeholder="Enter YouTube API Key"
                secretKey="yt_key"
              />
              <CredentialInput
                label="Channel ID"
                value={youtube.channel_id}
                onChange={(v) => setYoutube(prev => ({ ...prev, channel_id: v }))}
                placeholder="Enter Your Channel ID"
              />
            </PlatformCard>

            {/* LinkedIn */}
            <PlatformCard
              title="LinkedIn"
              icon={Linkedin}
              color="bg-blue-700"
              isEnabled={linkedin.is_enabled}
              onToggle={(checked) => setLinkedin(prev => ({ ...prev, is_enabled: checked }))}
              onSave={() => saveCredentials('LinkedIn', linkedin, 'linkedin')}
              onTest={() => testConnection('linkedin')}
            >
              <CredentialInput
                label="Client ID"
                value={linkedin.client_id}
                onChange={(v) => setLinkedin(prev => ({ ...prev, client_id: v }))}
                placeholder="Enter LinkedIn Client ID"
              />
              <CredentialInput
                label="Client Secret"
                value={linkedin.client_secret}
                onChange={(v) => setLinkedin(prev => ({ ...prev, client_secret: v }))}
                placeholder="Enter Client Secret"
                secretKey="linkedin_secret"
              />
              <CredentialInput
                label="Access Token"
                value={linkedin.access_token}
                onChange={(v) => setLinkedin(prev => ({ ...prev, access_token: v }))}
                placeholder="Enter Access Token"
                secretKey="linkedin_token"
              />
              <CredentialInput
                label="Organization ID"
                value={linkedin.organization_id}
                onChange={(v) => setLinkedin(prev => ({ ...prev, organization_id: v }))}
                placeholder="Enter Organization/Company ID"
              />
            </PlatformCard>
          </div>
        )}

        {/* Lead Scraping Tab */}
        {activeTab === 'lead-scraping' && (
          <div className="space-y-6">
            {/* Enable/Disable */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Autonomous Lead Generation</h3>
                  <p className="text-gray-600 text-sm">AI-powered lead scraping from social media and business directories</p>
                </div>
                <label className="flex items-center gap-3 cursor-pointer">
                  <span className="text-sm text-gray-600">Enable Scraping</span>
                  <div className={`relative w-14 h-7 rounded-full transition-colors ${
                    leadScraping.is_enabled ? 'bg-green-500' : 'bg-gray-300'
                  }`}>
                    <input
                      type="checkbox"
                      checked={leadScraping.is_enabled}
                      onChange={(e) => setLeadScraping(prev => ({ ...prev, is_enabled: e.target.checked }))}
                      className="sr-only"
                    />
                    <div className={`absolute top-1 w-5 h-5 bg-white rounded-full shadow transition-transform ${
                      leadScraping.is_enabled ? 'translate-x-8' : 'translate-x-1'
                    }`} />
                  </div>
                </label>
              </div>

              {/* Settings Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Scraping Frequency</label>
                  <select
                    value={leadScraping.scraping_frequency}
                    onChange={(e) => setLeadScraping(prev => ({ ...prev, scraping_frequency: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="hourly">Hourly</option>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Max Leads Per Day</label>
                  <input
                    type="number"
                    value={leadScraping.max_leads_per_day}
                    onChange={(e) => setLeadScraping(prev => ({ ...prev, max_leads_per_day: parseInt(e.target.value) || 50 }))}
                    min="10"
                    max="500"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="mt-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={leadScraping.auto_follow_up}
                    onChange={(e) => setLeadScraping(prev => ({ ...prev, auto_follow_up: e.target.checked }))}
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <span className="text-sm text-gray-700">Auto-trigger follow-up emails for new leads</span>
                </label>
              </div>
            </div>

            {/* Target Cities */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <MapPin className="w-5 h-5 text-blue-600" />
                Target Cities
              </h3>
              
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Metro Cities</h4>
                <div className="flex flex-wrap gap-2">
                  {availableCities.metro?.map(city => (
                    <label key={city} className="flex items-center gap-2 px-3 py-1 bg-gray-100 rounded-full cursor-pointer hover:bg-gray-200">
                      <input
                        type="checkbox"
                        checked={leadScraping.target_cities?.includes(city)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setLeadScraping(prev => ({ ...prev, target_cities: [...(prev.target_cities || []), city] }));
                          } else {
                            setLeadScraping(prev => ({ ...prev, target_cities: prev.target_cities?.filter(c => c !== city) || [] }));
                          }
                        }}
                        className="w-3 h-3"
                      />
                      <span className="text-sm">{city}</span>
                    </label>
                  ))}
                </div>
              </div>
              
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Tier 2 Cities</h4>
                <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
                  {availableCities.tier2?.map(city => (
                    <label key={city} className="flex items-center gap-2 px-3 py-1 bg-gray-100 rounded-full cursor-pointer hover:bg-gray-200">
                      <input
                        type="checkbox"
                        checked={leadScraping.target_cities?.includes(city)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setLeadScraping(prev => ({ ...prev, target_cities: [...(prev.target_cities || []), city] }));
                          } else {
                            setLeadScraping(prev => ({ ...prev, target_cities: prev.target_cities?.filter(c => c !== city) || [] }));
                          }
                        }}
                        className="w-3 h-3"
                      />
                      <span className="text-sm">{city}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            {/* Keywords */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Search className="w-5 h-5 text-blue-600" />
                Search Keywords
              </h3>
              
              <div className="flex flex-wrap gap-2 max-h-40 overflow-y-auto">
                {availableKeywords?.map(keyword => (
                  <label key={keyword} className="flex items-center gap-2 px-3 py-1 bg-blue-50 rounded-full cursor-pointer hover:bg-blue-100">
                    <input
                      type="checkbox"
                      checked={leadScraping.keywords?.includes(keyword)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setLeadScraping(prev => ({ ...prev, keywords: [...(prev.keywords || []), keyword] }));
                        } else {
                          setLeadScraping(prev => ({ ...prev, keywords: prev.keywords?.filter(k => k !== keyword) || [] }));
                        }
                      }}
                      className="w-3 h-3"
                    />
                    <span className="text-sm text-blue-800">{keyword}</span>
                  </label>
                ))}
              </div>
              
              <p className="text-sm text-gray-500 mt-3">
                Selected: {leadScraping.keywords?.length || 0} keywords
              </p>
            </div>

            {/* Business Types */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Users className="w-5 h-5 text-blue-600" />
                B2B Target Business Types
              </h3>
              
              <div className="flex flex-wrap gap-2">
                {availableBusinessTypes?.map(type => (
                  <label key={type} className="flex items-center gap-2 px-3 py-1 bg-green-50 rounded-full cursor-pointer hover:bg-green-100">
                    <input
                      type="checkbox"
                      checked={leadScraping.business_types?.includes(type)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setLeadScraping(prev => ({ ...prev, business_types: [...(prev.business_types || []), type] }));
                        } else {
                          setLeadScraping(prev => ({ ...prev, business_types: prev.business_types?.filter(t => t !== type) || [] }));
                        }
                      }}
                      className="w-3 h-3"
                    />
                    <span className="text-sm text-green-800">{type}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Save Button */}
            <div className="flex justify-end">
              <button
                onClick={saveLeadScrapingSettings}
                disabled={saving}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 disabled:opacity-50"
              >
                <Save className="w-5 h-5" />
                Save Lead Scraping Settings
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminSettings;
