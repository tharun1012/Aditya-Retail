import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  Calculator, TrendingUp, Store, Building2, PieChart, 
  Download, FileSpreadsheet, AlertCircle, CheckCircle,
  MapPin, Users, DollarSign, Target, BarChart3, ArrowRight,
  Loader2, ChevronDown, ChevronUp, Info, Search, Star
} from 'lucide-react';


const ROICalculator = () => {
  const [activeTab, setActiveTab] = useState('prefeasibility');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [stores, setStores] = useState([]);
  const [centralOverhead, setCentralOverhead] = useState({});
  const [expandedSections, setExpandedSections] = useState({});
  const [competitorResult, setCompetitorResult] = useState(null);
  const [competitorLoading, setCompetitorLoading] = useState(false);
  const [competitorLocation, setCompetitorLocation] = useState('');
  const [competitorRadius, setCompetitorRadius] = useState(5);

  // Pre-feasibility form
  const [prefeasibilityForm, setPrefeasibilityForm] = useState({
    city: '',
    city_tier: 'tier_2_city',
    store_size_sqft: 500,
    store_type: 'standard',
    product_categories: ['washing-machine', 'refrigerator', 'chimney'],
    investment_budget: '',
    target_monthly_revenue: '',
    use_historical_data: true
  });

  // Breakeven form
  const [breakevenForm, setBreakevenForm] = useState({
    store_name: '',
    monthly_rent: '',
    security_deposit: '',
    interior_setup_cost: '',
    initial_inventory: '',
    staff_salaries: '',
    utilities: '',
    other_expenses: '',
    expected_gross_margin: 0.20,
    target_breakeven_years: 2
  });

  // Store analysis form
  const [storeAnalysisForm, setStoreAnalysisForm] = useState({
    store_id: '',
    period_months: 12
  });

  const tabs = [
    { id: 'prefeasibility', label: 'Pre-Feasibility', icon: Target, color: 'blue' },
    { id: 'breakeven', label: 'Breakeven Calculator', icon: Calculator, color: 'green' },
    { id: 'existing', label: 'Existing Store ROI', icon: Store, color: 'purple' },
    { id: 'overview', label: 'Business Overview', icon: Building2, color: 'orange' },
    { id: 'competitors', label: 'Competitor Analysis', icon: MapPin, color: 'red' }
  ];

  const categories = [
    'washing-machine', 'refrigerator', 'chimney', 'gas-hob', 
    'dishwasher', 'oven', 'microwave', 'sink'
  ];

  useEffect(() => {
    fetchStores();
    fetchCentralOverhead();
  }, []);

  const fetchStores = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/roi-calculator/stores`);
      const data = await response.json();
      if (data.status === 'success') {
        setStores(data.stores);
      }
    } catch (error) {
      console.error('Error fetching stores:', error);
    }
  };

  const fetchCentralOverhead = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/roi-calculator/central-overhead`);
      const data = await response.json();
      if (data.status === 'success') {
        setCentralOverhead(data.data);
      }
    } catch (error) {
      console.error('Error fetching overhead:', error);
    }
  };

  const handlePrefeasibilitySubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const response = await fetch(`${BACKEND_URL}/api/roi-calculator/pre-feasibility`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...prefeasibilityForm,
          investment_budget: prefeasibilityForm.investment_budget ? parseFloat(prefeasibilityForm.investment_budget) : null,
          target_monthly_revenue: prefeasibilityForm.target_monthly_revenue ? parseFloat(prefeasibilityForm.target_monthly_revenue) : null
        })
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ status: 'error', message: error.message });
    } finally {
      setLoading(false);
    }
  };

  const handleBreakevenSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const response = await fetch(`${BACKEND_URL}/api/roi-calculator/breakeven`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...breakevenForm,
          monthly_rent: parseFloat(breakevenForm.monthly_rent),
          security_deposit: parseFloat(breakevenForm.security_deposit),
          interior_setup_cost: parseFloat(breakevenForm.interior_setup_cost),
          initial_inventory: parseFloat(breakevenForm.initial_inventory),
          staff_salaries: parseFloat(breakevenForm.staff_salaries),
          utilities: parseFloat(breakevenForm.utilities),
          other_expenses: parseFloat(breakevenForm.other_expenses || 0)
        })
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ status: 'error', message: error.message });
    } finally {
      setLoading(false);
    }
  };

  const handleStoreAnalysis = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const response = await fetch(`${BACKEND_URL}/api/roi-calculator/existing-store`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(storeAnalysisForm)
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ status: 'error', message: error.message });
    } finally {
      setLoading(false);
    }
  };

  const handleBusinessOverview = async () => {
    setLoading(true);
    setResult(null);
    try {
      const response = await fetch(`${BACKEND_URL}/api/roi-calculator/business-overview?period_months=12`);
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ status: 'error', message: error.message });
    } finally {
      setLoading(false);
    }
  };

  const handleCompetitorSearch = async (e) => {
    e.preventDefault();
    setCompetitorLoading(true);
    setCompetitorResult(null);
    try {
      const response = await fetch(`${BACKEND_URL}/api/roi-calculator/competitor-analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          location: competitorLocation,
          radius_km: competitorRadius
        })
      });
      const data = await response.json();
      setCompetitorResult(data);
    } catch (error) {
      setCompetitorResult({ status: 'error', message: error.message });
    } finally {
      setCompetitorLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const renderPrefeasibilityForm = () => (
    <form onSubmit={handlePrefeasibilitySubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">City Name</label>
          <input
            type="text"
            value={prefeasibilityForm.city}
            onChange={(e) => setPrefeasibilityForm({...prefeasibilityForm, city: e.target.value})}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., Mumbai, Pune"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">City Tier</label>
          <select
            value={prefeasibilityForm.city_tier}
            onChange={(e) => setPrefeasibilityForm({...prefeasibilityForm, city_tier: e.target.value})}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="tier_1_city">Tier 1 (Metro - Mumbai, Delhi, Bangalore)</option>
            <option value="tier_2_city">Tier 2 (Pune, Jaipur, Lucknow)</option>
            <option value="tier_3_city">Tier 3 (Smaller cities)</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Store Size (sq.ft.)</label>
          <input
            type="number"
            value={prefeasibilityForm.store_size_sqft}
            onChange={(e) => setPrefeasibilityForm({...prefeasibilityForm, store_size_sqft: parseInt(e.target.value)})}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            min="100"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Store Type</label>
          <select
            value={prefeasibilityForm.store_type}
            onChange={(e) => setPrefeasibilityForm({...prefeasibilityForm, store_type: e.target.value})}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="premium">Premium Showroom</option>
            <option value="standard">Standard Retail</option>
            <option value="budget">Budget Setup</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Investment Budget (Optional)</label>
          <input
            type="number"
            value={prefeasibilityForm.investment_budget}
            onChange={(e) => setPrefeasibilityForm({...prefeasibilityForm, investment_budget: e.target.value})}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., 2500000"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Target Monthly Revenue (Optional)</label>
          <input
            type="number"
            value={prefeasibilityForm.target_monthly_revenue}
            onChange={(e) => setPrefeasibilityForm({...prefeasibilityForm, target_monthly_revenue: e.target.value})}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., 1500000"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Product Categories</label>
        <div className="flex flex-wrap gap-2">
          {categories.map(cat => (
            <button
              key={cat}
              type="button"
              onClick={() => {
                const cats = prefeasibilityForm.product_categories.includes(cat)
                  ? prefeasibilityForm.product_categories.filter(c => c !== cat)
                  : [...prefeasibilityForm.product_categories, cat];
                setPrefeasibilityForm({...prefeasibilityForm, product_categories: cats});
              }}
              className={`px-3 py-1 rounded-full text-sm ${
                prefeasibilityForm.product_categories.includes(cat)
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {cat.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </button>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          checked={prefeasibilityForm.use_historical_data}
          onChange={(e) => setPrefeasibilityForm({...prefeasibilityForm, use_historical_data: e.target.checked})}
          className="rounded"
        />
        <label className="text-sm text-gray-700">Use historical data from existing stores (if available)</label>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
      >
        {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Calculator className="w-5 h-5" />}
        Generate Pre-Feasibility Analysis
      </button>
    </form>
  );

  const renderBreakevenForm = () => (
    <form onSubmit={handleBreakevenSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">Store Name</label>
          <input
            type="text"
            value={breakevenForm.store_name}
            onChange={(e) => setBreakevenForm({...breakevenForm, store_name: e.target.value})}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
            placeholder="e.g., Aditya Retail - Pune Branch"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Monthly Rent (₹)</label>
          <input
            type="number"
            value={breakevenForm.monthly_rent}
            onChange={(e) => setBreakevenForm({...breakevenForm, monthly_rent: e.target.value})}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Security Deposit (₹)</label>
          <input
            type="number"
            value={breakevenForm.security_deposit}
            onChange={(e) => setBreakevenForm({...breakevenForm, security_deposit: e.target.value})}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Interior & Setup Cost (₹)</label>
          <input
            type="number"
            value={breakevenForm.interior_setup_cost}
            onChange={(e) => setBreakevenForm({...breakevenForm, interior_setup_cost: e.target.value})}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Initial Inventory (₹)</label>
          <input
            type="number"
            value={breakevenForm.initial_inventory}
            onChange={(e) => setBreakevenForm({...breakevenForm, initial_inventory: e.target.value})}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Monthly Staff Salaries (₹)</label>
          <input
            type="number"
            value={breakevenForm.staff_salaries}
            onChange={(e) => setBreakevenForm({...breakevenForm, staff_salaries: e.target.value})}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Monthly Utilities (₹)</label>
          <input
            type="number"
            value={breakevenForm.utilities}
            onChange={(e) => setBreakevenForm({...breakevenForm, utilities: e.target.value})}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Other Monthly Expenses (₹)</label>
          <input
            type="number"
            value={breakevenForm.other_expenses}
            onChange={(e) => setBreakevenForm({...breakevenForm, other_expenses: e.target.value})}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Expected Gross Margin (%)</label>
          <input
            type="number"
            value={breakevenForm.expected_gross_margin * 100}
            onChange={(e) => setBreakevenForm({...breakevenForm, expected_gross_margin: parseFloat(e.target.value) / 100})}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
            min="1"
            max="100"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Target Breakeven (Years)</label>
          <select
            value={breakevenForm.target_breakeven_years}
            onChange={(e) => setBreakevenForm({...breakevenForm, target_breakeven_years: parseInt(e.target.value)})}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
          >
            <option value={1}>1 Year</option>
            <option value={2}>2 Years</option>
            <option value={3}>3 Years</option>
            <option value={4}>4 Years</option>
            <option value={5}>5 Years</option>
          </select>
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
      >
        {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <TrendingUp className="w-5 h-5" />}
        Calculate Breakeven
      </button>
    </form>
  );

  const renderExistingStoreForm = () => (
    <form onSubmit={handleStoreAnalysis} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Select Store</label>
          <select
            value={storeAnalysisForm.store_id}
            onChange={(e) => setStoreAnalysisForm({...storeAnalysisForm, store_id: e.target.value})}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
            required
          >
            <option value="">Select a store...</option>
            {stores.map(store => (
              <option key={store.id} value={store.id}>{store.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Analysis Period</label>
          <select
            value={storeAnalysisForm.period_months}
            onChange={(e) => setStoreAnalysisForm({...storeAnalysisForm, period_months: parseInt(e.target.value)})}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
          >
            <option value={3}>Last 3 Months</option>
            <option value={6}>Last 6 Months</option>
            <option value={12}>Last 12 Months</option>
            <option value={24}>Last 24 Months</option>
          </select>
        </div>
      </div>

      <button
        type="submit"
        disabled={loading || !storeAnalysisForm.store_id}
        className="w-full py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
      >
        {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <BarChart3 className="w-5 h-5" />}
        Analyze Store Performance
      </button>
    </form>
  );

  const renderBusinessOverview = () => (
    <div className="space-y-6">
      <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
        <h3 className="font-semibold text-orange-800 mb-2">📊 Business Overview</h3>
        <p className="text-sm text-orange-700">
          Get consolidated ROI analysis across all your stores, including central overhead tracking.
        </p>
      </div>

      <button
        onClick={handleBusinessOverview}
        disabled={loading}
        className="w-full py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors flex items-center justify-center gap-2"
      >
        {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Building2 className="w-5 h-5" />}
        Generate Business Overview
      </button>
    </div>
  );

  const renderCompetitorAnalysis = () => (
    <div className="space-y-6">
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <h3 className="font-semibold text-red-800 mb-2">🗺️ Competitor Analysis</h3>
        <p className="text-sm text-red-700">
          Find competitor home appliance stores near your target location using Google Maps.
        </p>
      </div>

      <form onSubmit={handleCompetitorSearch} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">Location / Address</label>
            <input
              type="text"
              value={competitorLocation}
              onChange={(e) => setCompetitorLocation(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500"
              placeholder="e.g., Baner, Pune or specific address"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Search Radius (km)</label>
            <select
              value={competitorRadius}
              onChange={(e) => setCompetitorRadius(parseInt(e.target.value))}
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500"
            >
              <option value={2}>2 km</option>
              <option value={5}>5 km</option>
              <option value={10}>10 km</option>
              <option value={15}>15 km</option>
              <option value={20}>20 km</option>
            </select>
          </div>
        </div>

        <button
          type="submit"
          disabled={competitorLoading || !competitorLocation}
          className="w-full py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {competitorLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
          Search Competitors
        </button>
      </form>

      {/* Competitor Results */}
      {competitorResult && (
        <div className="mt-6">
          {competitorResult.status === 'error' ? (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center gap-2 text-red-800">
                <AlertCircle className="w-5 h-5" />
                <span className="font-medium">Error: {competitorResult.message}</span>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="font-semibold text-gray-900">
                  Found {competitorResult.competitors_found} competitors near {competitorResult.location}
                </h4>
                {competitorResult.coordinates && (
                  <span className="text-sm text-gray-500">
                    📍 {competitorResult.coordinates.lat.toFixed(4)}, {competitorResult.coordinates.lng.toFixed(4)}
                  </span>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {competitorResult.competitors?.map((competitor, idx) => (
                  <div key={idx} className="bg-white border rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h5 className="font-semibold text-gray-900">{competitor.name}</h5>
                        <p className="text-sm text-gray-600 mt-1 flex items-start gap-1">
                          <MapPin className="w-4 h-4 flex-shrink-0 mt-0.5" />
                          {competitor.address}
                        </p>
                      </div>
                      {competitor.rating && (
                        <div className="flex items-center gap-1 bg-yellow-100 px-2 py-1 rounded">
                          <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                          <span className="font-semibold text-yellow-700">{competitor.rating}</span>
                        </div>
                      )}
                    </div>
                    {competitor.user_ratings_total && (
                      <p className="text-xs text-gray-500 mt-2">
                        {competitor.user_ratings_total} reviews
                      </p>
                    )}
                    {competitor.types && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {competitor.types.slice(0, 3).map((type, i) => (
                          <span key={i} className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded">
                            {type.replace(/_/g, ' ')}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );

  const renderResult = () => {
    if (!result) return null;

    if (result.status === 'error') {
      return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mt-6">
          <div className="flex items-center gap-2 text-red-800">
            <AlertCircle className="w-5 h-5" />
            <span className="font-medium">Error: {result.message}</span>
          </div>
        </div>
      );
    }

    return (
      <div className="mt-8 space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-bold text-gray-900">Analysis Results</h3>
          <button
            onClick={() => {
              const dataStr = JSON.stringify(result, null, 2);
              const blob = new Blob([dataStr], { type: 'application/json' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `roi_report_${new Date().toISOString().split('T')[0]}.json`;
              a.click();
            }}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
          >
            <Download className="w-4 h-4" />
            Export JSON
          </button>
        </div>

        {/* Pre-feasibility Results */}
        {result.analysis_type === 'pre_feasibility' && (
          <div className="space-y-4">
            {/* Revenue Projections */}
            <div className="bg-blue-50 rounded-lg p-4">
              <h4 className="font-semibold text-blue-800 mb-3">💰 Revenue Projections</h4>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">{formatCurrency(result.revenue_projections.estimated_monthly_revenue)}</p>
                  <p className="text-sm text-gray-600">Estimated Monthly</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-600">{formatCurrency(result.revenue_projections.min_revenue)}</p>
                  <p className="text-sm text-gray-600">Minimum</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">{formatCurrency(result.revenue_projections.max_revenue)}</p>
                  <p className="text-sm text-gray-600">Maximum</p>
                </div>
              </div>
            </div>

            {/* Rent Recommendations */}
            <div className="bg-green-50 rounded-lg p-4">
              <h4 className="font-semibold text-green-800 mb-3">🏠 Rent Recommendations</h4>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <p className="text-xl font-bold text-green-600">{formatCurrency(result.rent_recommendations.recommended_rent)}</p>
                  <p className="text-sm text-gray-600">Recommended</p>
                </div>
                <div className="text-center">
                  <p className="text-lg text-gray-600">{formatCurrency(result.rent_recommendations.rent_range_min)}</p>
                  <p className="text-sm text-gray-600">Min Range</p>
                </div>
                <div className="text-center">
                  <p className="text-lg text-gray-600">{formatCurrency(result.rent_recommendations.rent_range_max)}</p>
                  <p className="text-sm text-gray-600">Max Range</p>
                </div>
              </div>
            </div>

            {/* Investment Summary */}
            <div className="bg-purple-50 rounded-lg p-4">
              <h4 className="font-semibold text-purple-800 mb-3">💼 Investment Required</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {Object.entries(result.setup_investment).map(([key, value]) => (
                  <div key={key} className={`p-2 rounded ${key === 'total_investment' ? 'bg-purple-200 col-span-2 md:col-span-3' : 'bg-white'}`}>
                    <p className={`font-bold ${key === 'total_investment' ? 'text-xl text-purple-800' : 'text-gray-800'}`}>
                      {formatCurrency(value)}
                    </p>
                    <p className="text-xs text-gray-600">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Profitability */}
            <div className="bg-amber-50 rounded-lg p-4">
              <h4 className="font-semibold text-amber-800 mb-3">📈 Profitability Analysis</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-xl font-bold text-amber-600">{result.profitability_analysis.blended_gross_margin}</p>
                  <p className="text-sm text-gray-600">Gross Margin</p>
                </div>
                <div className="text-center">
                  <p className="text-xl font-bold text-green-600">{formatCurrency(result.profitability_analysis.monthly_net_profit)}</p>
                  <p className="text-sm text-gray-600">Monthly Profit</p>
                </div>
                <div className="text-center">
                  <p className="text-xl font-bold text-blue-600">{result.profitability_analysis.breakeven_months}</p>
                  <p className="text-sm text-gray-600">Breakeven (Months)</p>
                </div>
                <div className="text-center">
                  <p className="text-xl font-bold text-purple-600">{result.profitability_analysis.annual_roi}</p>
                  <p className="text-sm text-gray-600">Annual ROI</p>
                </div>
              </div>
            </div>

            {/* Recommendations */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-semibold text-gray-800 mb-3">💡 Recommendations</h4>
              <ul className="space-y-2">
                {result.recommendations.map((rec, idx) => (
                  <li key={idx} className="text-sm text-gray-700">{rec}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Breakeven Results */}
        {result.analysis_type === 'breakeven' && (
          <div className="space-y-4">
            <div className="bg-green-50 rounded-lg p-4">
              <h4 className="font-semibold text-green-800 mb-3">🎯 Breakeven Targets</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center bg-white p-3 rounded">
                  <p className="text-xl font-bold text-green-600">{formatCurrency(result.breakeven_targets.monthly_breakeven_revenue)}</p>
                  <p className="text-sm text-gray-600">Monthly Breakeven</p>
                </div>
                <div className="text-center bg-white p-3 rounded">
                  <p className="text-xl font-bold text-blue-600">{formatCurrency(result.breakeven_targets.daily_breakeven_revenue)}</p>
                  <p className="text-sm text-gray-600">Daily Target</p>
                </div>
                <div className="text-center bg-white p-3 rounded">
                  <p className="text-xl font-bold text-purple-600">{result.breakeven_targets.estimated_breakeven_month || 'N/A'}</p>
                  <p className="text-sm text-gray-600">Breakeven Month</p>
                </div>
                <div className="text-center bg-white p-3 rounded">
                  <p className="text-xl font-bold text-amber-600">{formatCurrency(result.investment_summary.total_investment)}</p>
                  <p className="text-sm text-gray-600">Total Investment</p>
                </div>
              </div>
            </div>

            {/* Year-wise Projections */}
            <div className="bg-white border rounded-lg overflow-hidden">
              <h4 className="font-semibold text-gray-800 p-4 bg-gray-50">📊 Year-wise Projections</h4>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="px-4 py-2 text-left">Year</th>
                      <th className="px-4 py-2 text-right">Revenue</th>
                      <th className="px-4 py-2 text-right">Net Profit</th>
                      <th className="px-4 py-2 text-right">Cumulative</th>
                      <th className="px-4 py-2 text-right">ROI %</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.year_wise_projections.map(proj => (
                      <tr key={proj.year} className="border-t">
                        <td className="px-4 py-2">Year {proj.year}</td>
                        <td className="px-4 py-2 text-right">{formatCurrency(proj.revenue)}</td>
                        <td className="px-4 py-2 text-right text-green-600">{formatCurrency(proj.net_profit)}</td>
                        <td className={`px-4 py-2 text-right ${proj.cumulative_profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {formatCurrency(proj.cumulative_profit)}
                        </td>
                        <td className="px-4 py-2 text-right">{proj.roi_percentage}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Sensitivity Analysis */}
            <div className="bg-white border rounded-lg overflow-hidden">
              <h4 className="font-semibold text-gray-800 p-4 bg-gray-50">📉 Sensitivity Analysis</h4>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="px-4 py-2 text-left">Scenario</th>
                      <th className="px-4 py-2 text-right">Monthly Revenue</th>
                      <th className="px-4 py-2 text-right">Monthly Profit</th>
                      <th className="px-4 py-2 text-right">Annual ROI</th>
                      <th className="px-4 py-2 text-center">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.sensitivity_analysis.map((scenario, idx) => (
                      <tr key={idx} className="border-t">
                        <td className="px-4 py-2">{scenario.scenario}</td>
                        <td className="px-4 py-2 text-right">{formatCurrency(scenario.monthly_revenue)}</td>
                        <td className={`px-4 py-2 text-right ${scenario.monthly_profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {formatCurrency(scenario.monthly_profit)}
                        </td>
                        <td className="px-4 py-2 text-right">{scenario.annual_roi}%</td>
                        <td className="px-4 py-2 text-center">
                          <span className={`px-2 py-1 rounded text-xs ${scenario.status === 'Profitable' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                            {scenario.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Existing Store Results */}
        {result.analysis_type === 'existing_store' && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg text-center">
                <p className="text-2xl font-bold text-blue-600">{formatCurrency(result.revenue_analysis.total_revenue)}</p>
                <p className="text-sm text-gray-600">Total Revenue</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg text-center">
                <p className="text-2xl font-bold text-green-600">{formatCurrency(result.profitability.gross_profit)}</p>
                <p className="text-sm text-gray-600">Gross Profit</p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg text-center">
                <p className="text-2xl font-bold text-purple-600">{result.profitability.gross_margin_percentage}%</p>
                <p className="text-sm text-gray-600">Gross Margin</p>
              </div>
              <div className="bg-amber-50 p-4 rounded-lg text-center">
                <p className="text-2xl font-bold text-amber-600">{result.performance_rating.overall_rating}</p>
                <p className="text-sm text-gray-600">Performance</p>
              </div>
            </div>

            {/* Tax Analysis */}
            <div className="bg-teal-50 rounded-lg p-4">
              <h4 className="font-semibold text-teal-800 mb-3">🧾 ITC/GST Analysis</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-lg font-bold text-teal-600">{formatCurrency(result.tax_analysis.output_gst_collected)}</p>
                  <p className="text-xs text-gray-600">Output GST</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-bold text-green-600">{formatCurrency(result.tax_analysis.input_tax_credit_available)}</p>
                  <p className="text-xs text-gray-600">ITC Available</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-bold text-amber-600">{formatCurrency(result.tax_analysis.net_gst_payable)}</p>
                  <p className="text-xs text-gray-600">Net GST Payable</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-bold text-blue-600">{result.tax_analysis.itc_utilization_percentage}%</p>
                  <p className="text-xs text-gray-600">ITC Utilization</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Business Overview Results */}
        {result.analysis_type === 'business_overview' && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg text-center">
                <p className="text-2xl font-bold text-blue-600">{result.store_count}</p>
                <p className="text-sm text-gray-600">Total Stores</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg text-center">
                <p className="text-2xl font-bold text-green-600">{formatCurrency(result.consolidated_financials.total_revenue)}</p>
                <p className="text-sm text-gray-600">Total Revenue</p>
              </div>
              <div className="bg-amber-50 p-4 rounded-lg text-center">
                <p className="text-2xl font-bold text-amber-600">{formatCurrency(result.consolidated_financials.central_overhead)}</p>
                <p className="text-sm text-gray-600">Central Overhead</p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg text-center">
                <p className="text-2xl font-bold text-purple-600">{formatCurrency(result.consolidated_financials.net_business_profit)}</p>
                <p className="text-sm text-gray-600">Net Profit</p>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Calculator className="w-8 h-8 text-blue-600" />
            ROI Calculator
          </h1>
          <p className="text-gray-600 mt-2">
            Store viability analysis, breakeven calculations, and performance tracking
          </p>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-sm border mb-6">
          <div className="border-b overflow-x-auto">
            <div className="flex min-w-max">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => { setActiveTab(tab.id); setResult(null); }}
                  className={`flex items-center gap-2 px-4 md:px-6 py-4 font-medium transition-colors whitespace-nowrap ${
                    activeTab === tab.id 
                      ? `text-${tab.color}-600 border-b-2 border-${tab.color}-600 bg-${tab.color}-50` 
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <tab.icon className="w-5 h-5" />
                  <span className="hidden sm:inline">{tab.label}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="p-4 md:p-6">
            {activeTab === 'prefeasibility' && renderPrefeasibilityForm()}
            {activeTab === 'breakeven' && renderBreakevenForm()}
            {activeTab === 'existing' && renderExistingStoreForm()}
            {activeTab === 'overview' && renderBusinessOverview()}
            {activeTab === 'competitors' && renderCompetitorAnalysis()}
          </div>
        </div>

        {/* Results */}
        {renderResult()}
      </div>
    </div>
  );
};

export default ROICalculator;
